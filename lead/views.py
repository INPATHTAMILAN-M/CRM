# # lead/views.py

# import os
# import requests
# from django.conf import settings
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.db import transaction

# # local model for storing apollo responses
# from lead.models import ApolloLead

# APOLLO_SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/api_search"
# APOLLO_BULK_MATCH_URL = "https://api.apollo.io/v1/people/bulk_match"


# def get_apollo_api_key():
#     return os.getenv("APOLLO_API_KEY") or getattr(settings, "APOLLO_API_KEY", None)


# @api_view(["POST"])
# def get_apollo_leads(request):
#     api_key = get_apollo_api_key()

#     if not api_key:
#         return Response(
#             {"error": "APOLLO_API_KEY not configured"},
#             status=500
#         )

#     # Request payload from client
#     payload = dict(request.data or {})

#     # Default pagination
#     payload.setdefault("page", 1)
#     payload.setdefault("per_page", 2)

#     # Apollo headers (IMPORTANT)
#     headers = {
#         "Content-Type": "application/json",
#         "X-Api-Key": api_key
#     }

#     try:
#         # =========================
#         # STEP 1: SEARCH PEOPLE
#         # =========================
#         search_resp = requests.post(
#             APOLLO_SEARCH_URL,
#             json=payload,
#             headers=headers,
#             timeout=45
#         )

#         # Handle non-JSON / HTML response safely
#         content_type = search_resp.headers.get("Content-Type", "")

#         if search_resp.status_code != 200:
#             return Response({
#                 "error": "Apollo search failed",
#                 "status_code": search_resp.status_code,
#                 "response": search_resp.text[:500]
#             }, status=400)

#         if "application/json" not in content_type:
#             return Response({
#                 "error": "Invalid response from Apollo (not JSON)",
#                 "response": search_resp.text[:500]
#             }, status=400)

#         search_data = search_resp.json()
#         people = search_data.get("people", [])

#         # Extract IDs
#         details = [{"id": p["id"]} for p in people if p.get("id")]

#         if not details:
#             return Response({
#                 "success": False,
#                 "message": "No people found",
#                 "search_response": search_data
#             }, status=404)

#         # =========================
#         # STEP 2: BULK MATCH
#         # =========================
#         bulk_payload = {"details": details}

#         bulk_resp = requests.post(
#             APOLLO_BULK_MATCH_URL,
#             json=bulk_payload,
#             headers=headers,
#             timeout=60
#         )

#         if bulk_resp.status_code != 200:
#             return Response({
#                 "error": "Apollo bulk match failed",
#                 "status_code": bulk_resp.status_code,
#                 "response": bulk_resp.text[:500]
#             }, status=400)

#         # Parse bulk response and ingest matches into ApolloLead
#         bulk_data = bulk_resp.json()

#         def _extract_matches(payload):
#             if not isinstance(payload, dict):
#                 return []
#             if 'matches' in payload and isinstance(payload['matches'], list):
#                 return payload['matches']
#             if 'data' in payload and isinstance(payload['data'], dict) and 'matches' in payload['data'] and isinstance(payload['data']['matches'], list):
#                 return payload['data']['matches']
#             # Fallback: some apollo bulk responses list people under 'people'
#             if 'people' in payload and isinstance(payload['people'], list):
#                 return payload['people']
#             return []

#         matches = _extract_matches(bulk_data)
#         created = []
#         updated = []

#         if matches:
#             with transaction.atomic():
#                 model_fields = {f.name for f in ApolloLead._meta.get_fields()}
#                 for item in matches:
#                     external_id = item.get('id') or item.get('external_id')
#                     if not external_id:
#                         continue

#                     defaults = {
#                         'first_name': item.get('first_name'),
#                         'last_name': item.get('last_name'),
#                         'full_name': item.get('name') or item.get('full_name'),
#                         'title': item.get('title'),
#                         'headline': item.get('headline'),
#                         'linkedin_url': item.get('linkedin_url'),
#                         'photo_url': item.get('photo_url'),
#                         'twitter_url': item.get('twitter_url'),
#                         'github_url': item.get('github_url'),
#                         'facebook_url': item.get('facebook_url'),
#                         'email': item.get('email'),
#                         'email_status': item.get('email_status'),
#                         'street_address': item.get('street_address'),
#                         'city': item.get('city'),
#                         'state': item.get('state'),
#                         'country': item.get('country'),
#                         'postal_code': item.get('postal_code'),
#                         'formatted_address': item.get('formatted_address'),
#                         'time_zone': item.get('time_zone'),
#                         'organization_id': (item.get('organization') or {}).get('id') if item.get('organization') else item.get('organization_id'),
#                         'organization_name': (item.get('organization') or {}).get('name') if item.get('organization') else None,
#                         'organization': item.get('organization'),
#                         'employment_history': item.get('employment_history'),
#                         'departments': item.get('departments'),
#                         'subdepartments': item.get('subdepartments'),
#                         'seniority': item.get('seniority'),
#                         'functions': item.get('functions'),
#                         'raw_json': item,
#                     }

#                     filtered_defaults = {k: v for k, v in defaults.items() if k in model_fields}

#                     obj, created_flag = ApolloLead.objects.update_or_create(external_id=external_id, defaults=filtered_defaults)
#                     if created_flag:
#                         created.append(external_id)
#                     else:
#                         updated.append(external_id)

#         return Response({
#             "success": True,
#             "count": len(details),
#             "ingested": {"created": len(created), "updated": len(updated)},
#             "data": bulk_data
#         })

#     except requests.exceptions.Timeout:
#         return Response(
#             {"error": "Apollo API timeout"},
#             status=400
#         )

#     except requests.exceptions.RequestException as e:
#         return Response(
#             {"error": str(e)},
#             status=400
#         )

#     except ValueError:
#         return Response(
#             {"error": "Invalid JSON response from Apollo"},
#             status=400
#         )


import os
import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from decimal import Decimal

# local model for storing apollo responses
from lead.models import ApolloLead
from lead.models_apollo import ApolloPagination



from django.utils import timezone
from django.db.models import Sum, Count, Q, F
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from accounts.models import Lead_Source
from lead.models import Lead, Opportunity, Task, Contact
from accounts.models import MonthlyTarget, UserTarget
from django.contrib.auth.models import User

APOLLO_SEARCH_URL = "https://api.apollo.io/api/v1/mixed_people/api_search"
APOLLO_BULK_MATCH_URL = "https://api.apollo.io/v1/people/bulk_match"


def get_apollo_api_key():
    return os.getenv("APOLLO_API_KEY") or getattr(settings, "APOLLO_API_KEY", None)


@api_view(["POST"])
def get_apollo_leads(request):
    api_key = get_apollo_api_key()

    if not api_key:
        return Response(
            {"error": "APOLLO_API_KEY not configured"},
            status=500
        )

    # Request payload from client
    payload = dict(request.data or {})

    # Default pagination
    payload.setdefault("page", 1)
    payload.setdefault("per_page", 2)

    page = payload.get("page")
    per_page = payload.get("per_page")

    # தேடல் அளவுருக்களை வரிசைப்படுத்தி ஒப்பிடுவதற்கான வசதி
    def _get_sorted(key):
        val = payload.get(key, [])
        return sorted(val) if isinstance(val, list) else val

    history_filters = {
        "person_titles": _get_sorted("person_titles"),
        "person_locations": _get_sorted("person_locations"),
        "organization_num_employees_ranges": _get_sorted("organization_num_employees_ranges"),
        "organization_industries": _get_sorted("organization_industries"),
        "page": page,
        "per_page": per_page
    }

    # ஏற்கனவே இந்தப் பக்கம் இருந்தால், அடுத்த கிடைக்கக்கூடிய பக்கத்தைக் கண்டறியவும் (Auto-increment logic)
    original_page = page
    skipped_pages = []
    while ApolloPagination.objects.filter(**history_filters).exists():
        skipped_pages.append(page)
        page += 1
        payload["page"] = page
        history_filters["page"] = page

    # Apollo headers (IMPORTANT)
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key
    }

    try:
        # =========================
        # STEP 1: SEARCH PEOPLE
        # =========================
        search_resp = requests.post(
            APOLLO_SEARCH_URL,
            json=payload,
            headers=headers,
            timeout=45
        )

        # Handle non-JSON / HTML response safely
        content_type = search_resp.headers.get("Content-Type", "")

        if search_resp.status_code != 200:
            return Response({
                "error": "Apollo search failed",
                "status_code": search_resp.status_code,
                "response": search_resp.text[:500]
            }, status=400)

        if "application/json" not in content_type:
            return Response({
                "error": "Invalid response from Apollo (not JSON)",
                "response": search_resp.text[:500]
            }, status=400)

        search_data = search_resp.json()
        people = search_data.get("people", [])

        # Extract IDs
        details = [{"id": p["id"]} for p in people if p.get("id")]

        if not details:
            return Response({
                "success": False,
                "message": "No people found",
                "search_response": search_data
            }, status=404)

        # =========================
        # STEP 2: BULK MATCH
        # =========================
        bulk_payload = {"details": details}

        bulk_resp = requests.post(
            APOLLO_BULK_MATCH_URL,
            json=bulk_payload,
            headers=headers,
            timeout=60
        )

        if bulk_resp.status_code != 200:
            return Response({
                "error": "Apollo bulk match failed",
                "status_code": bulk_resp.status_code,
                "response": bulk_resp.text[:500]
            }, status=400)

        # Parse bulk response and ingest matches into ApolloLead
        bulk_data = bulk_resp.json()

        def _extract_matches(payload):
            if not isinstance(payload, dict):
                return []
            if 'matches' in payload and isinstance(payload['matches'], list):
                return payload['matches']
            if 'data' in payload and isinstance(payload['data'], dict) and 'matches' in payload['data'] and isinstance(payload['data']['matches'], list):
                return payload['data']['matches']
            # Fallback: some apollo bulk responses list people under 'people'
            if 'people' in payload and isinstance(payload['people'], list):
                return payload['people']
            return []

        matches = _extract_matches(bulk_data)
        created = []
        updated = []

        if matches:
            with transaction.atomic():
                model_fields = {f.name for f in ApolloLead._meta.get_fields()}
                for item in matches:
                    external_id = item.get('id') or item.get('external_id')
                    if not external_id:
                        continue

                    defaults = {
                        'first_name': item.get('first_name'),
                        'last_name': item.get('last_name'),
                        'full_name': item.get('name') or item.get('full_name'),
                        'title': item.get('title'),
                        'headline': item.get('headline'),
                        'linkedin_url': item.get('linkedin_url'),
                        'photo_url': item.get('photo_url'),
                        'twitter_url': item.get('twitter_url'),
                        'github_url': item.get('github_url'),
                        'facebook_url': item.get('facebook_url'),
                        'email': item.get('email'),
                        'email_status': item.get('email_status'),
                        'street_address': item.get('street_address'),
                        'city': item.get('city'),
                        'state': item.get('state'),
                        'country': item.get('country'),
                        'postal_code': item.get('postal_code'),
                        'formatted_address': item.get('formatted_address'),
                        'time_zone': item.get('time_zone'),
                        'organization_id': (item.get('organization') or {}).get('id') if item.get('organization') else item.get('organization_id'),
                        'organization_name': (item.get('organization') or {}).get('name') if item.get('organization') else None,
                        'organization': item.get('organization'),
                        'employment_history': item.get('employment_history'),
                        'departments': item.get('departments'),
                        'subdepartments': item.get('subdepartments'),
                        'seniority': item.get('seniority'),
                        'functions': item.get('functions'),
                        'raw_json': item,
                    }

                    filtered_defaults = {k: v for k, v in defaults.items() if k in model_fields}

                    obj, created_flag = ApolloLead.objects.update_or_create(external_id=external_id, defaults=filtered_defaults)
                    if created_flag:
                        created.append(external_id)
                    else:
                        updated.append(external_id)

        # வெற்றிகரமாக முடிந்ததும் தேடல் வரலாற்றில் சேமிக்கவும்
        ApolloPagination.objects.create(**history_filters)

        return Response({
            "success": True,
            "page_requested": original_page,
            "page_fetched": page,
            "skipped_pages": skipped_pages,
            "count": len(details),
            "ingested": {"created": len(created), "updated": len(updated)},
            "data": bulk_data
        })

    except requests.exceptions.Timeout:
        return Response(
            {"error": "Apollo API timeout"},
            status=400
        )

    except requests.exceptions.RequestException as e:
        return Response(
            {"error": str(e)},
            status=400
        )

    except ValueError:
        return Response(
            {"error": "Invalid JSON response from Apollo"},
            status=400
        )

    
@api_view(["GET"])
def dashboard(request):
    """GET /api/dashboard

    Optional query params: start_date, end_date (YYYY-MM-DD)
    All metrics use created_on (or created_at) within the date range where applicable.
    """

    # parse dates / presets
    preset = (request.query_params.get('preset') or request.query_params.get('period') or '').strip().lower()
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    try:
        if preset:
            now = timezone.now()
            end = now
            if preset in ('6months', '6_months', '6-months', '6m', '6'):
                start = now - relativedelta(months=6)
            elif preset in ('1month', '1_month', '1-month', '1m', '1'):
                start = now - relativedelta(months=1)
            elif preset in ('7days', '7_days', '7-days', '7d', '7'):
                start = now - timedelta(days=7)
            elif preset in ('1year', '1_year', 'last_year', '12months', '12_months', '1y'):
                start = now - relativedelta(years=1)
            else:
                # unknown preset — fall back to explicit dates or very old date
                start = datetime(1970, 1, 1)
        else:
            if start_date:
                start = datetime.fromisoformat(start_date)
            else:
                # No filter — show all historical data
                start = datetime(1970, 1, 1)
            if end_date:
                end = datetime.fromisoformat(end_date) + timedelta(days=1)
            else:
                now_t = timezone.now()
                end = now_t.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        # Ensure timezone-aware datetimes for safe comparisons with `timezone.now()`
        if timezone.is_naive(start):
            start = timezone.make_aware(start)
        if timezone.is_naive(end):
            end = timezone.make_aware(end)
    except Exception:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD or valid preset."}, status=400)

    # Optional user filter
    user_id = request.query_params.get('user_id') or request.query_params.get('user')
    user_obj = None
    if user_id:
        try:
            user_obj = User.objects.filter(id=int(user_id)).first()
        except Exception:
            user_obj = None

    # Cards
    leads_q = Lead.objects.filter(is_active=True, created_on__gte=start, created_on__lt=end)
    if user_obj:
        leads_q = leads_q.filter(lead_owner=user_obj)
    total_leads = leads_q.count()

    converted_leads_q = leads_q.filter(lead_status__name__iexact='converted')
    converted_leads = converted_leads_q.count()

    lead_conversion_rate = (converted_leads / total_leads * 100) if total_leads else 0

    # total_actual_revenue is computed after the per-user revenue loop below
    # to ensure it matches the sum of per-user actual_revenue values.
    won_ids = [34]  # 'Deal Won' status ID

    # Total opportunities (all statuses)
    all_opps_q = Opportunity.objects.filter(created_on__gte=start, created_on__lt=end)
    if user_obj:
        all_opps_q = all_opps_q.filter(owner=user_obj)
    total_opportunities = all_opps_q.count()

    # Converted (won) opportunities and conversion rate
    converted_opps = all_opps_q.filter(opportunity_status_id__in=won_ids).count()
    opportunity_conversion_rate = (converted_opps / total_opportunities * 100) if total_opportunities else 0

    # Tasks
    tasks_q = Task.objects.filter(is_active=True, deleted=False, created_on__gte=start, created_on__lt=end)
    if user_obj:
        tasks_q = tasks_q.filter(Q(created_by=user_obj) | Q(contact__assigned_to=user_obj))
    total_tasks = tasks_q.count()

    now = timezone.now()
    overdue_q = tasks_q.filter(task_date_time__lt=now, is_active=True)
    overdue_tasks = overdue_q.count()
    overdue_rate = (overdue_tasks / total_tasks * 100) if total_tasks else 0

    # Active targets (count of monthly targets + active user targets within range)
    mt_q = MonthlyTarget.objects.filter(created_at__gte=start, created_at__lt=end)
    ut_q = UserTarget.objects.filter(created_at__gte=start, created_at__lt=end, is_active=True)
    if user_obj:
        mt_q = mt_q.filter(user=user_obj)
        ut_q = ut_q.filter(user=user_obj)
    monthly_targets_count = mt_q.count()
    user_targets_count = ut_q.count()
    active_targets = monthly_targets_count + user_targets_count

    # Team average achievement will be calculated after building revenue_vs_user


    # Users to exclude from all responses
    EXCLUDED_USERNAMES = {'root', 'support@irepute.in'}

    def display_name(u):
        """Return first name if set, otherwise the username local part (before @)."""
        if u.first_name.strip():
            return u.first_name.strip()
        # Strip email domain if username looks like an email
        username = u.username
        if '@' in username:
            username = username.split('@')[0]
        return username

    # Helper: get cumulative target for a user up to cap_dt.
    # Monthly targets store a running total from the user's start — so the value
    # at the cap month IS the total target up to that point. start_date only
    # scopes actual_revenue, not the target.
    def get_cumulative_target(u, from_dt, cap_dt):
        """
        Returns the cumulative target up to cap_dt (the end of the requested range).
        Monthly targets are running totals, so we just return the latest MT row
        on or before cap_dt.
        from_dt is accepted for API compatibility but does not affect the result.
        """
        cap_year, cap_month = cap_dt.year, cap_dt.month

        mt_end = (
            MonthlyTarget.objects.filter(user=u, year__lt=cap_year) |
            MonthlyTarget.objects.filter(user=u, year=cap_year, month__lte=cap_month)
        ).order_by('-year', '-month').first()

        if not mt_end:
            return None  # no MT data — caller falls back to annual

        return float(mt_end.target_amount)

    # Determine whether the caller supplied an explicit date range (not just defaults)
    has_date_filter = bool(request.query_params.get('start_date') or
                           request.query_params.get('end_date') or
                           request.query_params.get('preset') or
                           request.query_params.get('period'))

    # user loop removed as it is now redundant

    # Charts
    lead_distribution = leads_q.values(status_name=F('lead_status__name')).annotate(count=Count('id')).order_by('-count')
    lead_distribution_status = [{'status': d['status_name'] or 'Unknown', 'count': d['count']} for d in lead_distribution]

    sources = leads_q.values(source_name=F('lead_source__source')).annotate(total=Count('id'))
    conv_by_source = []
    for s in sources:
        source_name = s['source_name'] or 'Unknown'
        total = s['total']
        converted = Lead.objects.filter(lead_source__source=source_name, lead_status__name__iexact='converted', created_on__gte=start, created_on__lt=end).count()
        rate = (converted / total * 100) if total else 0
        conv_by_source.append({'source': source_name, 'total': total, 'converted': converted, 'conversion_rate': rate})

    contacts_q = Contact.objects.filter(created_on__gte=start, created_on__lt=end)
    if user_obj:
        contacts_q = contacts_q.filter(assigned_to=user_obj)
    contact_dist = contacts_q.values(status_name=F('status__status')).annotate(count=Count('id')).order_by('-count')
    contact_status_distribution = [{'status': c['status_name'] or 'Unknown', 'count': c['count']} for c in contact_dist]

    users_with_targets = User.objects.exclude(username__in=EXCLUDED_USERNAMES)
    if user_obj:
        users_with_targets = User.objects.filter(id=user_obj.id).exclude(username__in=EXCLUDED_USERNAMES)
    revenue_vs_user = []
    now_for_target = timezone.now()

    for u in users_with_targets:
        # (actual revenue calculation moved below after determining target ranges)

        # Determine the user's start month for display purposes
        earliest_mt = MonthlyTarget.objects.filter(user=u).order_by('year', 'month').first()
        if earliest_mt:
            user_start = (earliest_mt.year, earliest_mt.month)
        else:
            dj = u.date_joined
            user_start = (dj.year, dj.month)

        target_amount = 0
        breakdown = {
            'method': None,
            'monthly_sum': 0,
            'months_count': 0,
            'annual_target': None,
            'computed_annual_based': 0,
            'target_start': f"{user_start[0]}-{user_start[1]:02d}",
        }

        if has_date_filter:
            # Scoped to the requested date range
            range_cap = end - relativedelta(days=1)
            range_from = start
        else:
            # No filter: full range from user's first MT up to now
            range_from = start.tzinfo and datetime(user_start[0], user_start[1], 1, tzinfo=start.tzinfo) or timezone.make_aware(datetime(user_start[0], user_start[1], 1))
            range_cap = now_for_target

        # If the user's start month is after the cap month, they have no target in this range
        user_start_dt = datetime(user_start[0], user_start[1], 1, tzinfo=range_cap.tzinfo)
        if user_start_dt > range_cap:
            revenue_vs_user.append({
                'username': display_name(u),
                'target_amount': 0.0,
                'actual_revenue': 0.0,
                'achievement_percentage': 0.0,
                'target_breakdown': {**breakdown, 'method': None},
            })
            continue

        # Count months in range for breakdown info
        range_months = []
        cy, cm = range_from.year, range_from.month
        cap_ym = (range_cap.year, range_cap.month)
        while (cy, cm) <= cap_ym:
            range_months.append((cy, cm))
            cm += 1
            if cm > 12:
                cm = 1
                cy += 1
        breakdown['months_count'] = len(range_months)

        range_target = get_cumulative_target(u, range_from, range_cap)
        if range_target is not None:
            target_amount = range_target
            breakdown['monthly_sum'] = target_amount
            breakdown['method'] = 'monthly'

        if not target_amount:
            ut = UserTarget.objects.filter(user=u, is_active=True).first()
            if ut:
                months_count = len(range_months) or 1
                try:
                    annual = float(ut.target)
                    breakdown['annual_target'] = float(annual)
                    computed = (annual / 12.0) * months_count
                    target_amount = computed
                    breakdown['computed_annual_based'] = float(computed)
                    breakdown['method'] = 'annual'
                except Exception:
                    target_amount = 0

        # Weighted revenue calculation — sum per-month achieved amounts
        # using the exact same logic as MonthlyTargetSerializer.get_achieved_amount
        # to ensure dashboard actual_revenue matches monthly-targets achieved_amount
        actual = Decimal('0.00')
        for r_year, r_month in range_months:
            m_start = date(r_year, r_month, 1)
            m_end = (m_start + relativedelta(months=1)) - relativedelta(days=1)
            qs = Opportunity.objects.filter(
                opportunity_status_id=34,
                is_active=True,
                closing_date__range=(m_start, m_end),
            )
            filters_with_weights = [
                (Q(lead__created_by=u) & Q(lead__assigned_to=u), Decimal('1')),
                (Q(lead__created_by=u) & ~Q(lead__assigned_to=u), Decimal('0.5')),
                (~Q(lead__created_by=u) & Q(lead__assigned_to=u), Decimal('0.5')),
            ]
            for condition, weight in filters_with_weights:
                val = qs.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
                actual += Decimal(str(val)) * weight

        achievement = (float(actual) / float(target_amount) * 100) if target_amount and float(target_amount) > 0 else 0
        revenue_vs_user.append({
            'username': display_name(u),
            'target_amount': float(target_amount),
            'actual_revenue': float(actual),
            'achievement_percentage': achievement,
            'target_breakdown': breakdown,
        })

    # Compute total_actual_revenue from per-user results (consistent with monthly-targets achieved_amount)
    total_actual_revenue = sum(item['actual_revenue'] for item in revenue_vs_user)

    valid_achievements = [item['achievement_percentage'] for item in revenue_vs_user if item['target_amount'] > 0]
    team_avg_achievement = sum(valid_achievements) / len(valid_achievements) if valid_achievements else 0

    # Opportunity chart 1 — count and total value per status
    opp_status_qs = (
        all_opps_q
        .values(status_name=F('opportunity_status__name'))
        .annotate(count=Count('id'), total_value=Sum('opportunity_value'))
        .order_by('-count')
    )
    opportunity_status_chart = [
        {
            'status': row['status_name'] or 'Unknown',
            'count': row['count'],
            'total_value': float(row['total_value'] or 0),
        }
        for row in opp_status_qs
    ]

    # Opportunity chart 2 — conversion rate by source (based on opportunity's lead source)
    opp_sources_qs = (
        all_opps_q
        .values(source_name=F('lead__lead_source__source'))
        .annotate(total=Count('id'))
    )
    opp_conv_by_source = []
    for row in opp_sources_qs:
        source_name = row['source_name'] or 'Unknown'
        total = row['total']
        won_count = all_opps_q.filter(
            lead__lead_source__source=row['source_name'],
            opportunity_status_id__in=won_ids,
        ).count()
        rate = (won_count / total * 100) if total else 0
        opp_conv_by_source.append({
            'source': source_name,
            'total': total,
            'won': won_count,
            'conversion_rate': round(rate, 2),
        })
    opp_conv_by_source.sort(key=lambda x: x['total'], reverse=True)

    # Common cards and charts (always included)
    common_cards = {
        'total_actual_revenue': float(total_actual_revenue),
        'total_tasks': total_tasks,
        'overdue_tasks': overdue_tasks,
        'overdue_rate': overdue_rate,
        'active_targets': active_targets,
        'team_avg_achievement': team_avg_achievement,
    }
    common_charts = {
        'revenue_target_vs_actual_by_user': revenue_vs_user,
    }

    opportunity_mode = request.query_params.get('opportunity', '').strip().lower() in ('true', '1', 'yes')

    if opportunity_mode:
        data = {
            'cards': {
                **common_cards,
                'total_opportunities': total_opportunities,
                'converted_opportunities': converted_opps,
                'opportunity_conversion_rate': round(opportunity_conversion_rate, 2),
            },
            'charts': {
                **common_charts,
                'opportunity_status': opportunity_status_chart,
                'opportunity_conversion_rate_by_source': opp_conv_by_source,
            }
        }
    else:
        data = {
            'cards': {
                **common_cards,
                'total_leads': total_leads,
                'converted_leads': converted_leads,
                'lead_conversion_rate': lead_conversion_rate,
            },
            'charts': {
                **common_charts,
                'lead_distribution_status': lead_distribution_status,
                'conversion_rate_by_source': conv_by_source,
                'contact_status_distribution': contact_status_distribution,
            }
        }

    return Response(data)
