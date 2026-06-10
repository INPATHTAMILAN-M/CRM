from datetime import timedelta
from dateutil import parser
from django.conf import settings
from django.utils import timezone
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import Task

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = getattr(settings, 'GOOGLE_CALENDAR_ID', 'primary')
SERVICE_ACCOUNT_FILE = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_FILE', None)
TOKEN_FILE = getattr(settings, 'GOOGLE_CALENDAR_TOKEN_FILE', None)
CREDENTIALS_FILE = getattr(settings, 'GOOGLE_CALENDAR_CREDENTIALS_FILE', None)
GOOGLE_IMPERSONATED_USER = getattr(settings, 'GOOGLE_IMPERSONATED_USER', None)


def get_credentials():
    if SERVICE_ACCOUNT_FILE:
        if not SERVICE_ACCOUNT_FILE:
            raise ValueError('Google service account file is not configured in settings.')
        creds = service_account.Credentials.from_service_account_file(
            str(SERVICE_ACCOUNT_FILE),
            scopes=SCOPES,
            subject=GOOGLE_IMPERSONATED_USER,
        )
        return creds

    if not TOKEN_FILE or not CREDENTIALS_FILE:
        raise ValueError('Google Calendar credentials are not configured in settings.')

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w', encoding='utf-8') as token_file:
            token_file.write(creds.to_json())

    return creds


def get_calendar_service():
    creds = get_credentials()
    return build('calendar', 'v3', credentials=creds)


def _make_aware(dt):
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_default_timezone())
    return dt


def _build_event_body(task: Task) -> dict:
    start_dt = _make_aware(task.task_date_time)
    if not start_dt:
        raise ValueError('Task must have task_date_time before syncing to Google Calendar.')

    end_dt = start_dt + timedelta(hours=1)
    summary = f"{task.task_type or 'Task'}: {task.contact.name or 'Task'}"
    description_lines = []
    if task.contact:
        description_lines.append(f"Contact: {task.contact.name}")
        if task.contact.email_id:
            description_lines.append(f"Email: {task.contact.email_id}")
        if task.contact.phone_number:
            description_lines.append(f"Phone: {task.contact.phone_number}")
    if task.remark:
        description_lines.append(f"Remark: {task.remark}")
    if task.task_detail:
        description_lines.append('Details:')
        description_lines.append(task.task_detail)

    body = {
        'summary': summary,
        'description': '\n'.join(description_lines).strip(),
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': str(timezone.get_current_timezone()),
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': str(timezone.get_current_timezone()),
        },
        'extendedProperties': {
            'shared': {
                'task_id': str(task.id),
            }
        },
    }

    if task.contact and task.contact.email_id and not SERVICE_ACCOUNT_FILE:
        body['attendees'] = [{'email': task.contact.email_id}]

    return body


def create_or_update_google_event(task: Task) -> None:
    if not task.task_date_time or task.deleted or not task.is_active:
        return

    service = get_calendar_service()
    body = _build_event_body(task)
    needs_insert = not task.google_event_id

    try:
        if not needs_insert:
            try:
                service.events().patch(
                    calendarId=CALENDAR_ID,
                    eventId=task.google_event_id,
                    body=body,
                ).execute()
                task.google_calendar_synced = True
                task.save(update_fields=['google_calendar_synced'])
                return
            except HttpError as exc:
                if hasattr(exc, 'resp') and getattr(exc.resp, 'status', None) in (404, 410):
                    task.google_event_id = None
                    task.google_calendar_synced = False
                    task.save(update_fields=['google_event_id', 'google_calendar_synced'])
                    needs_insert = True
                else:
                    task.google_calendar_synced = False
                    task.save(update_fields=['google_calendar_synced'])
                    raise

        if needs_insert:
            event = service.events().insert(
                calendarId=CALENDAR_ID,
                body=body,
                sendUpdates='none',
            ).execute()
            task.google_event_id = event.get('id')
            task.google_calendar_synced = True
            task.save(update_fields=['google_event_id', 'google_calendar_synced'])
    except HttpError:
        task.google_calendar_synced = False
        task.save(update_fields=['google_calendar_synced'])
        raise


def delete_google_event(task: Task) -> None:
    if not task.google_event_id:
        return

    try:
        service = get_calendar_service()
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=task.google_event_id,
        ).execute()
    except HttpError:
        pass
    finally:
        task.google_event_id = None
        task.google_calendar_synced = False
        task.save(update_fields=['google_event_id', 'google_calendar_synced'])


def sync_google_events() -> int:
    service = get_calendar_service()
    now = timezone.now()
    time_min = (now - timedelta(days=30)).isoformat()
    time_max = (now + timedelta(days=365)).isoformat()
    updated_count = 0

    events = []
    page_token = None
    while True:
        response = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy='updated',
            showDeleted=True,
            pageToken=page_token,
        ).execute()
        events.extend(response.get('items', []))
        page_token = response.get('nextPageToken')
        if not page_token:
            break

    for event in events:
        props = event.get('extendedProperties', {}).get('shared', {})
        task_id = props.get('task_id')
        if not task_id:
            continue

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            continue

        if event.get('status') == 'cancelled':
            if not task.deleted or task.is_active or task.google_event_id:
                task.deleted = True
                task.is_active = False
                task.google_event_id = None
                task.save(update_fields=['deleted', 'is_active', 'google_event_id'])
                updated_count += 1
            continue

        start_value = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
        if not start_value:
            continue

        event_updated = event.get('updated')
        if event_updated:
            event_updated_dt = parser.isoparse(event_updated)
            local_updated = getattr(task, 'updated_on', task.created_on)
            if local_updated and event_updated_dt <= local_updated:
                continue

        parsed_start = parser.isoparse(start_value)
        task.task_date_time = parsed_start
        task.google_event_id = event.get('id')

        description = event.get('description')
        if description:
            remark_value = None
            detail_value = description

            if 'Remark:' in description and 'Details:' in description:
                _, remainder = description.split('Remark:', 1)
                remark_part, detail_part = remainder.split('Details:', 1)
                remark_value = remark_part.strip()
                detail_value = detail_part.strip()
            elif 'Details:' in description:
                detail_value = description.split('Details:', 1)[1].strip()

            if remark_value is not None:
                task.remark = remark_value
            task.task_detail = detail_value
        else:
            task.task_detail = event.get('summary', task.task_detail)

        task.deleted = False
        task.is_active = True
        task.save(update_fields=['task_date_time', 'google_event_id', 'task_detail', 'remark', 'deleted', 'is_active'])
        updated_count += 1

    return updated_count
