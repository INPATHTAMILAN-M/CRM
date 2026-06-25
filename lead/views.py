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


# import os
# import requests
# from django.conf import settings
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.db import transaction
# from decimal import Decimal

# # local model for storing apollo responses
# from lead.models import ApolloLead
# from lead.models_apollo import ApolloPagination



# from django.utils import timezone
# from django.db.models import Sum, Count, Q, F
# from datetime import datetime, timedelta, date
# from dateutil.relativedelta import relativedelta
# from accounts.models import Lead_Source
# from lead.models import Lead, Opportunity, Task, Contact
# from accounts.models import MonthlyTarget, UserTarget
# from django.contrib.auth.models import User

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

#     page = payload.get("page")
#     per_page = payload.get("per_page")

#     # தேடல் அளவுருக்களை வரிசைப்படுத்தி ஒப்பிடுவதற்கான வசதி
#     def _get_sorted(key):
#         val = payload.get(key, [])
#         return sorted(val) if isinstance(val, list) else val

#     history_filters = {
#         "person_titles": _get_sorted("person_titles"),
#         "person_locations": _get_sorted("person_locations"),
#         "organization_num_employees_ranges": _get_sorted("organization_num_employees_ranges"),
#         "organization_industries": _get_sorted("organization_industries"),
#         "page": page,
#         "per_page": per_page
#     }

#     # ஏற்கனவே இந்தப் பக்கம் இருந்தால், அடுத்த கிடைக்கக்கூடிய பக்கத்தைக் கண்டறியவும் (Auto-increment logic)
#     original_page = page
#     skipped_pages = []
#     while ApolloPagination.objects.filter(**history_filters).exists():
#         skipped_pages.append(page)
#         page += 1
#         payload["page"] = page
#         history_filters["page"] = page

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

#         # வெற்றிகரமாக முடிந்ததும் தேடல் வரலாற்றில் சேமிக்கவும்
#         ApolloPagination.objects.create(**history_filters)

#         return Response({
#             "success": True,
#             "page_requested": original_page,
#             "page_fetched": page,
#             "skipped_pages": skipped_pages,
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

    
# @api_view(["GET"])
# def dashboard(request):
#     """GET /api/dashboard

#     Optional query params: start_date, end_date (YYYY-MM-DD)
#     All metrics use created_on (or created_at) within the date range where applicable.
#     """

#     # parse dates / presets
#     preset = (request.query_params.get('preset') or request.query_params.get('period') or '').strip().lower()
#     start_date = request.query_params.get('start_date')
#     end_date = request.query_params.get('end_date')

#     try:
#         if preset:
#             now = timezone.now()
#             end = now
#             if preset in ('6months', '6_months', '6-months', '6m', '6'):
#                 # Last 6 complete calendar months (1st of month, 6 months back → end of last month)
#                 first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#                 start = first_of_this_month - relativedelta(months=6)
#                 end = first_of_this_month
#             elif preset in ('1month', '1_month', '1-month', '1m', '1', 'current_month', 'this_month'):
#                 # Current month: from 1st of this month to end of this month
#                 start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#                 end = (start + relativedelta(months=1))
#             elif preset in ('last_month', 'lastmonth', 'last month', 'last-month'):
#                 # Previous month: from 1st to last day of last month
#                 first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#                 start = first_of_this_month - relativedelta(months=1)
#                 end = first_of_this_month
#             elif preset in ('7days', '7_days', '7-days', '7d', '7'):
#                 start = now - timedelta(days=7)
#             elif preset in ('1year', '1_year', 'last_year', '12months', '12_months', '1y'):
#                 # Last 12 complete calendar months
#                 first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#                 start = first_of_this_month - relativedelta(months=12)
#                 end = first_of_this_month
#             else:
#                 # unknown preset — fall back to explicit dates or very old date
#                 start = datetime(1970, 1, 1)
#         else:
#             if start_date:
#                 start = datetime.fromisoformat(start_date)
#             else:
#                 # No filter — show all historical data
#                 start = datetime(1970, 1, 1)
#             if end_date:
#                 end = datetime.fromisoformat(end_date) + timedelta(days=1)
#             else:
#                 now_t = timezone.now()
#                 end = now_t.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

#         # Ensure timezone-aware datetimes for safe comparisons with timezone.now()
#         if timezone.is_naive(start):
#             start = timezone.make_aware(start)
#         if timezone.is_naive(end):
#             end = timezone.make_aware(end)
#     except Exception:
#         return Response({"error": "Invalid date format. Use YYYY-MM-DD or valid preset."}, status=400)

#     # Optional user filter
#     user_id = request.query_params.get('user_id') or request.query_params.get('user')
#     is_team = request.query_params.get('team', '').lower() == 'true'
#     user_obj = None
#     is_admin = False
#     is_bdm = False
#     team_member_ids = []
#     if user_id:
#         try:
#             user_obj = User.objects.filter(id=int(user_id)).first()
#             if user_obj:
#                 is_admin = user_obj.groups.filter(name__iexact="Admin").exists()
#                 is_bdm = user_obj.groups.filter(name__iexact="BDM").exists()
#                 if is_bdm:
#                     from accounts.models import Teams
#                     user_team = Teams.objects.filter(bdm_user=user_obj).first()
#                     if user_team:
#                         team_member_ids = list(user_team.bde_user.values_list("id", flat=True))
#             else:
#                 user_id = None
#         except Exception:
#             user_id = None
#             user_obj = None

#     # Cards
#     leads_q = Lead.objects.filter(is_active=True, created_on__gte=start, created_on__lt=end)
#     if user_obj:
#         if is_admin:
#             if is_team:
#                 leads_q = leads_q.exclude(Q(created_by=user_obj) | Q(assigned_to=user_obj))
#             else:
#                 leads_q = leads_q.filter(Q(created_by=user_obj) | Q(assigned_to=user_obj))
#         elif is_bdm:
#             if is_team:
#                 leads_q = leads_q.filter(Q(created_by__in=team_member_ids) | Q(assigned_to__in=team_member_ids))
#             else:
#                 leads_q = leads_q.filter(Q(lead_owner=user_obj) | Q(created_by=user_obj) | Q(assigned_to=user_obj))
#         else:
#             leads_q = leads_q.filter(Q(assigned_to=user_obj) | Q(created_by=user_obj))
#     leads_q = leads_q.distinct()
#     total_leads = leads_q.count()

#     converted_leads_q = leads_q.filter(lead_status__name__iexact='converted')
#     converted_leads = converted_leads_q.count()

#     lead_conversion_rate = (converted_leads / total_leads * 100) if total_leads else 0

#     # Total actual revenue from won/converted opportunities
#     won_ids = [34]  # 'Deal Won' status ID
#     opportunities_q = Opportunity.objects.filter(is_active=True, closing_date__gte=start.date(), closing_date__lt=end.date(), opportunity_status_id__in=won_ids)
#     if user_obj:
#         if is_admin:
#             if is_team:
#                 opportunities_q = opportunities_q.exclude(Q(lead__created_by=user_obj) | Q(lead__assigned_to=user_obj))
#             else:
#                 opportunities_q = opportunities_q.filter(Q(lead__created_by=user_obj) | Q(lead__assigned_to=user_obj))
#         elif is_bdm:
#             if is_team:
#                 opportunities_q = opportunities_q.filter(Q(lead__assigned_to__in=team_member_ids) | Q(lead__created_by__in=team_member_ids))
#             else:
#                 opportunities_q = opportunities_q.filter(Q(lead__assigned_to=user_obj) | Q(lead__created_by=user_obj))
#         else:
#             opportunities_q = opportunities_q.filter(Q(lead__assigned_to=user_obj) | Q(lead__created_by=user_obj))
    
#     if user_obj and not is_team:
#         total_actual_revenue = opportunities_q.aggregate(total=Sum('opportunity_value'))['total'] or 0
#     else:
#         # Company-wide total
#         total_actual_revenue = opportunities_q.aggregate(total=Sum('opportunity_value'))['total'] or 0

#     # Total opportunities (all statuses)
#     all_opps_q = Opportunity.objects.filter(created_on__gte=start, created_on__lt=end)
#     if user_obj:
#         if is_admin:
#             if is_team:
#                 all_opps_q = all_opps_q.exclude(Q(lead__created_by=user_obj) | Q(lead__assigned_to=user_obj))
#             else:
#                 all_opps_q = all_opps_q.filter(Q(lead__created_by=user_obj) | Q(lead__assigned_to=user_obj))
#         elif is_bdm:
#             if is_team:
#                 all_opps_q = all_opps_q.filter(Q(lead__assigned_to__in=team_member_ids) | Q(lead__created_by__in=team_member_ids))
#             else:
#                 all_opps_q = all_opps_q.filter(Q(lead__assigned_to=user_obj) | Q(lead__created_by=user_obj))
#         else:
#             all_opps_q = all_opps_q.filter(Q(lead__assigned_to=user_obj) | Q(lead__created_by=user_obj))
#     total_opportunities = all_opps_q.count()

#     # Converted (won) opportunities and conversion rate
#     converted_opps = all_opps_q.filter(opportunity_status_id__in=won_ids).count()
#     opportunity_conversion_rate = (converted_opps / total_opportunities * 100) if total_opportunities else 0

#     # Tasks scoped to the requested date range
#     tasks_q = Task.objects.filter(is_active=True, created_on__gte=start, created_on__lt=end)
#     if user_obj:
#         if is_admin:
#             if is_team:
#                 tasks_q = tasks_q.exclude(Q(created_by=user_obj) | Q(task_task_assignments__assigned_to=user_obj))
#             else:
#                 tasks_q = tasks_q.filter(Q(created_by=user_obj) | Q(task_task_assignments__assigned_to=user_obj))
#         elif is_bdm:
#             if is_team:
#                 tasks_q = tasks_q.filter(created_by__in=team_member_ids)
#             else:
#                 tasks_q = tasks_q.filter(Q(task_task_assignments__assigned_to=user_obj.id) | Q(created_by=user_obj))
#         else:
#             tasks_q = tasks_q.filter(Q(task_task_assignments__assigned_to=user_obj.id) | Q(created_by=user_obj))
#     tasks_q = tasks_q.distinct()
#     total_tasks = tasks_q.count()

#     now = timezone.now()
#     overdue_q = tasks_q.filter(task_date_time__lt=now, is_active=True)
#     overdue_tasks = overdue_q.count()
#     overdue_rate = (overdue_tasks / total_tasks * 100) if total_tasks else 0

#     # Active targets (count of monthly targets + active user targets within range)
#     mt_q = MonthlyTarget.objects.filter(created_at__gte=start, created_at__lt=end)
#     ut_q = UserTarget.objects.filter(created_at__gte=start, created_at__lt=end, is_active=True)
#     if user_id:
#         if is_team:
#             mt_q = mt_q.exclude(user_id=user_id)
#             ut_q = ut_q.exclude(user_id=user_id)
#         else:
#             mt_q = mt_q.filter(user_id=user_id)
#             ut_q = ut_q.filter(user_id=user_id)
#     monthly_targets_count = mt_q.count()
#     user_targets_count = ut_q.count()
#     active_targets = monthly_targets_count + user_targets_count

#     # Team average achievement
#     users = User.objects.all()
#     user_achievements = []

#     # build months list for range (robust) and exclude future months (only up to last completed month)
#     def build_months_list(start_dt, end_dt):
#         s = start_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         last_inclusive = (end_dt - timedelta(days=1))
#         e = last_inclusive.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
#         months_list_local = []
#         cur = s
#         while cur <= e:
#             months_list_local.append((cur.year, cur.month))
#             cur = cur + relativedelta(months=1)
#         return months_list_local

#     months_list = build_months_list(start, end)
#     # exclude months strictly in the future (keep current month and all past months)
#     now = timezone.now()
#     current_month_tuple = (now.year, now.month)
#     months_list = [m for m in months_list if m <= current_month_tuple]
#     months = set(months_list)

#     # Users to exclude from all responses
#     EXCLUDED_USERNAMES = {'root', 'support@irepute.in'}

#     def display_name(u):
#         """Return first name if set, otherwise the username local part (before @)."""
#         if u.first_name.strip():
#             return u.first_name.strip()
#         # Strip email domain if username looks like an email
#         username = u.username
#         if '@' in username:
#             username = username.split('@')[0]
#         return username

#     # Helper: get cumulative target for a user up to cap_dt.
#     # Monthly targets store a running total from the user's start — so the value
#     # at the cap month IS the total target up to that point. start_date only
#     # scopes actual_revenue, not the target.
#     def get_cumulative_target(u, from_dt, cap_dt):
#         """
#         Returns the cumulative target up to cap_dt (the end of the requested range).
#         Monthly targets are running totals, so we just return the latest MT row
#         on or before cap_dt.
#         from_dt is accepted for API compatibility but does not affect the result.
#         """
#         cap_year, cap_month = cap_dt.year, cap_dt.month

#         mt_end = (
#             MonthlyTarget.objects.filter(user=u, year__lt=cap_year) |
#             MonthlyTarget.objects.filter(user=u, year=cap_year, month__lte=cap_month)
#         ).order_by('-year', '-month').first()

#         if not mt_end:
#             return None  # no MT data — caller falls back to annual

#         return float(mt_end.target_amount)

#     # Determine whether the caller supplied an explicit date range (not just defaults)
#     has_date_filter = bool(request.query_params.get('start_date') or
#                            request.query_params.get('end_date') or
#                            request.query_params.get('preset') or
#                            request.query_params.get('period'))

#     for u in users:
#         if u.username in EXCLUDED_USERNAMES:
#             continue
#         if user_id and is_team and u.id == int(user_id):
#             continue
        
#         # Weighted revenue calculation aligned with targets
#         actual = 0
#         opps_in_range_q = Opportunity.objects.filter(
#             is_active=True,
#             closing_date__gte=start.date(),
#             closing_date__lt=end.date(),
#             opportunity_status_id=34
#         )
#         # Exact same 4-filter logic as MonthlyTargetSerializer.get_achieved_amount
#         filters_with_weights = [
#             (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
#             (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
#             (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5),
#             (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5),
#         ]
#         for condition, weight in filters_with_weights:
#             val = opps_in_range_q.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
#             actual += float(val) * weight

#         target_sum = 0
#         if has_date_filter:
#             range_cap_u = end - relativedelta(days=1)
#         else:
#             range_cap_u = timezone.now()

#         # Skip users whose target starts after the cap month
#         earliest_mt_u = MonthlyTarget.objects.filter(user=u).order_by('year', 'month').first()
#         user_start_u = (earliest_mt_u.year, earliest_mt_u.month) if earliest_mt_u else (u.date_joined.year, u.date_joined.month)
#         user_start_dt_u = datetime(user_start_u[0], user_start_u[1], 1, tzinfo=range_cap_u.tzinfo)
#         if user_start_dt_u > range_cap_u:
#             user_achievements.append(0.0)
#             continue

#         range_target = get_cumulative_target(u, start, range_cap_u)

#         if range_target is not None:
#             target_sum = range_target
#         if not target_sum:
#             ut = UserTarget.objects.filter(user=u, is_active=True).first()
#             if ut:
#                 months_count = len(months) or 1
#                 try:
#                     annual = float(ut.target)
#                     target_sum = (annual / 12.0) * months_count
#                 except Exception:
#                     target_sum = 0

#         achievement_pct = (float(actual) / float(target_sum) * 100) if target_sum and float(target_sum) > 0 else 0
#         user_achievements.append(achievement_pct)

#     team_avg_achievement = (sum(user_achievements) / len(user_achievements)) if user_achievements else 0

#     # Charts
#     # Helper: merge actual counts with full master list, defaulting missing entries to 0
#     from lead.models import Lead_Status
#     from accounts.models import Lead_Source, Contact_Status, Stage as OppStage

#     # Lead distribution by status — show ALL active lead statuses
#     all_lead_statuses = list(Lead_Status.objects.filter(is_active=True).values_list('name', flat=True))
#     lead_dist_actual = {
#         d['status_name']: d['count']
#         for d in leads_q.values(status_name=F('lead_status__name')).annotate(count=Count('id'))
#     }
#     lead_distribution_status = [
#         {'status': s, 'count': lead_dist_actual.get(s, 0)}
#         for s in all_lead_statuses
#     ]
#     # Contacts (used by sources and contact charts)
#     contacts_q = Contact.objects.filter(is_active=True, created_on__gte=start, created_on__lt=end)
#     if user_obj:
#         if is_admin:
#             if is_team:
#                 contacts_q = contacts_q.exclude(Q(assigned_to=user_obj) | Q(created_by=user_obj))
#             else:
#                 contacts_q = contacts_q.filter(Q(assigned_to=user_obj) | Q(created_by=user_obj))
#         elif is_bdm:
#             if is_team:
#                 contacts_q = contacts_q.filter(Q(assigned_to__in=team_member_ids) | Q(created_by__in=team_member_ids))
#             else:
#                 contacts_q = contacts_q.filter(Q(assigned_to=user_obj) | Q(created_by=user_obj))
#         else:
#             contacts_q = contacts_q.filter(Q(assigned_to=user_obj) | Q(created_by=user_obj))
#     contact_dist = contacts_q.values(status_name=F('status__status')).annotate(count=Count('id')).order_by('-count')
#     # Show ALL active contact statuses, with 0 for missing ones
#     all_contact_statuses = list(Contact_Status.objects.filter(is_active=True).values_list('status', flat=True))
#     contact_dist_actual = {d['status_name']: d['count'] for d in contact_dist}
#     contact_status_distribution = [
#         {'status': s, 'count': contact_dist_actual.get(s, 0)}
#         for s in all_contact_statuses
#     ]
#     total_contacts = contacts_q.count()
#     contacts_without_lead = contacts_q.filter(lead__isnull=True, is_archive=False).count()
#     # contacts_without_lead = contacts_q.filter(lead__isnull=True).count()
#     contacts_with_lead = contacts_q.filter(lead__isnull=False).count()

#     # Lead-source distribution — show ALL active lead sources, with 0 for missing ones
#     all_lead_sources = list(Lead_Source.objects.filter(is_active=True).values_list('source', flat=True))
#     sources_actual = {
#         s['source_name']: s['total']
#         for s in leads_q.values(source_name=F('lead_source__source')).annotate(total=Count('id'))
#     }
#     conv_by_source = []
#     for source_name in all_lead_sources:
#         total = sources_actual.get(source_name, 0)
#         converted = leads_q.filter(lead_source__source=source_name, lead_status__name__iexact='converted').count()
#         rate = (converted / total * 100) if total else 0
#         conv_by_source.append({'source': source_name, 'total': total, 'converted': converted, 'conversion_rate': round(rate, 2)})

#     # All contacts source distribution — show ALL active lead sources
#     all_contacts_src_actual = {
#         s['source_name']: s['count']
#         for s in contacts_q.values(source_name=F('lead_source__source')).annotate(count=Count('id'))
#     }
#     all_contacts_source_dist = [
#         {'source': s, 'count': all_contacts_src_actual.get(s, 0)}
#         for s in all_lead_sources
#     ]

#     # Task type distribution (counts per task_type) for charts
#     task_types_q = tasks_q.values(type_name=F('task_type')).annotate(count=Count('id')).order_by('-count')
#     task_type_distribution = [{'task_type': t['type_name'] or 'Unknown', 'count': t['count']} for t in task_types_q]

#     # (contacts_q was defined earlier)
#     total_contacts = contacts_q.count()

#     users_with_targets = User.objects.exclude(username__in=EXCLUDED_USERNAMES)
#     if user_id:
#         if is_team:
#             users_with_targets = users_with_targets.exclude(id=user_id)
#         else:
#             users_with_targets = users_with_targets.filter(id=user_id)
#     revenue_vs_user = []
#     now_for_target = timezone.now()

#     # Financial year = Apr to Mar
#     # Current FY: Apr 2026 – Mar 2027
#     now_fy = timezone.now()
#     if now_fy.month >= 4:
#         fy_start_year = now_fy.year
#     else:
#         fy_start_year = now_fy.year - 1
#     fy_months = []
#     for i in range(12):
#         m = ((3 + i) % 12) + 1   # Apr=4 … Mar=3
#         y = fy_start_year if m >= 4 else fy_start_year + 1
#         fy_months.append((y, m))

#     # When user_id is given and not team → show month-by-month breakdown.
#     # With date filter: split across months in the given range.
#     # Without date filter: split across the current financial year (Apr–Mar).
#     user_fy_mode = bool(user_id) and not is_team

#     if user_fy_mode:
#         if has_date_filter or preset:
#             # Build month list from the requested date range
#             # Guard: if start is epoch fallback, use current month only
#             effective_start = start
#             if effective_start.year < 2000:
#                 effective_start = (end - relativedelta(months=1)).replace(day=1)
#             range_months_list = []
#             cy, cm = effective_start.year, effective_start.month
#             cap_ym = ((end - relativedelta(days=1)).year, (end - relativedelta(days=1)).month)
#             while (cy, cm) <= cap_ym:
#                 range_months_list.append((cy, cm))
#                 cm += 1
#                 if cm > 12:
#                     cm = 1
#                     cy += 1
#         else:
#             # No filter: use current financial year Apr–Mar
#             range_months_list = fy_months

#         for u in users_with_targets:
#             monthly_data = []
#             for (yr, mo) in range_months_list:
#                 month_start = timezone.make_aware(datetime(yr, mo, 1))
#                 month_end = timezone.make_aware(datetime(yr + 1, 1, 1) if mo == 12 else datetime(yr, mo + 1, 1))
#                 # Actual: same weighted logic as AnnualTargetAnalyticsViewSet._sum_achieved
#                 month_start_d = month_start.date()
#                 month_end_d = (month_end - timedelta(days=1)).date()
#                 qs = Opportunity.objects.filter(
#                     opportunity_status_id=34,
#                     is_active=True,
#                     closing_date__range=(month_start_d, month_end_d),
#                 )
#                 actual_mo = Decimal('0.00')
#                 for condition, weight in [
#                     (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
#                     (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
#                     (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), Decimal('0.5')),
#                     (~Q(lead__created_by=u) & Q(lead__assigned_to=u), Decimal('0.5')),
#                 ]:
#                     val = qs.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
#                     actual_mo += Decimal(str(val)) * Decimal(str(weight))
#                 actual_mo = float(actual_mo)
#                 # # Actual: won opps by lead.created_by closed in this month
#                 # actual_mo = float(Opportunity.objects.filter(
#                 #     is_active=True,
#                 #     closing_date__gte=month_start.date(),
#                 #     closing_date__lt=month_end.date(),
#                 #     opportunity_status_id=34,
#                 #     lead__created_by=u,
#                 # ).aggregate(total=Sum('opportunity_value'))['total'] or 0)

#                 # Target: use the MT value directly as stored (matches monthly target API)
#                 mt_this = MonthlyTarget.objects.filter(user=u, year=yr, month=mo).first()
#                 if mt_this:
#                     target_mo = float(mt_this.target_amount)
#                 else:
#                     # Fallback: annual / 12
#                     ut = UserTarget.objects.filter(user=u, is_active=True).first()
#                     target_mo = float(ut.target) / 12.0 if ut else 0.0

#                 achievement_mo = (actual_mo / target_mo * 100) if target_mo > 0 else 0.0
#                 monthly_data.append({
#                     'month': f"{yr}-{mo:02d}",
#                     'target_amount': round(target_mo, 2),
#                     'actual_revenue': round(actual_mo, 2),
#                     'achievement_percentage': round(achievement_mo, 2),
#                 })

#             revenue_vs_user.append({
#                 'username': display_name(u),
#                 'monthly_breakdown': monthly_data,
#             })

#     else:
#         for u in users_with_targets:
#             # Weighted revenue calculation aligned with targets
#             actual = 0
#             opps_in_range_q = Opportunity.objects.filter(
#                 is_active=True,
#                 closing_date__gte=start.date(),
#                 closing_date__lt=end.date(),
#                 opportunity_status_id=34
#             )
#             # Exact same 4-filter logic as MonthlyTargetSerializer.get_achieved_amount
#             filters_with_weights = [
#                 (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
#                 (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
#                 (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5),
#                 (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5),
#             ]
#             for condition, weight in filters_with_weights:
#                 val = opps_in_range_q.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
#                 actual += float(val) * weight

#             # Determine the user's start month for display purposes
#             earliest_mt = MonthlyTarget.objects.filter(user=u).order_by('year', 'month').first()
#             if earliest_mt:
#                 user_start = (earliest_mt.year, earliest_mt.month)
#             else:
#                 dj = u.date_joined
#                 user_start = (dj.year, dj.month)

#             target_amount = 0
#             breakdown = {
#                 'method': None,
#                 'monthly_sum': 0,
#                 'months_count': 0,
#                 'annual_target': None,
#                 'computed_annual_based': 0,
#                 'target_start': f"{user_start[0]}-{user_start[1]:02d}",
#             }

#             if has_date_filter:
#                 # Scoped to the requested date range
#                 range_cap = end - relativedelta(days=1)
#                 range_from = start
#             else:
#                 # No filter: full range from user's first MT up to now
#                 range_from = start.tzinfo and datetime(user_start[0], user_start[1], 1, tzinfo=start.tzinfo) or timezone.make_aware(datetime(user_start[0], user_start[1], 1))
#                 range_cap = now_for_target

#             # If the user's start month is after the cap month, they have no target in this range
#             user_start_dt = datetime(user_start[0], user_start[1], 1, tzinfo=range_cap.tzinfo)
#             if user_start_dt > range_cap:
#                 revenue_vs_user.append({
#                     'username': display_name(u),
#                     'target_amount': 0.0,
#                     'actual_revenue': 0.0,
#                     'achievement_percentage': 0.0,
#                     'target_breakdown': {**breakdown, 'method': None},
#                 })
#                 continue

#             # Count months in range for breakdown info
#             range_months = []
#             cy, cm = range_from.year, range_from.month
#             cap_ym = (range_cap.year, range_cap.month)
#             while (cy, cm) <= cap_ym:
#                 range_months.append((cy, cm))
#                 cm += 1
#                 if cm > 12:
#                     cm = 1
#                     cy += 1
#             breakdown['months_count'] = len(range_months)

#             range_target = get_cumulative_target(u, range_from, range_cap)
#             if range_target is not None:
#                 target_amount = range_target
#                 breakdown['monthly_sum'] = target_amount
#                 breakdown['method'] = 'monthly'

#             if not target_amount:
#                 ut = UserTarget.objects.filter(user=u, is_active=True).first()
#                 if ut:
#                     months_count = len(range_months) or 1
#                     try:
#                         annual = float(ut.target)
#                         breakdown['annual_target'] = float(annual)
#                         computed = (annual / 12.0) * months_count
#                         target_amount = computed
#                         breakdown['computed_annual_based'] = float(computed)
#                         breakdown['method'] = 'annual'
#                     except Exception:
#                         target_amount = 0

#             achievement = (float(actual) / float(target_amount) * 100) if target_amount and float(target_amount) > 0 else 0
#             revenue_vs_user.append({
#                 'username': display_name(u),
#                 'target_amount': float(target_amount),
#                 'actual_revenue': float(actual),
#                 'achievement_percentage': achievement,
#                 'target_breakdown': breakdown,
#             })

#     # Compute company-wide actual revenue as sum of achieved_amount from MonthlyTarget rows
#     total_actual_revenue = 0
#     try:
#         if months:
#             years = [y for y, m in months]
#             months_vals = [m for y, m in months]
#             mt_qs = MonthlyTarget.objects.filter(year__in=years, month__in=months_vals)
#             if user_id:
#                 if is_team:
#                     mt_qs = mt_qs.exclude(user_id=user_id)
#                 else:
#                     mt_qs = mt_qs.filter(user_id=user_id)
#             # Import serializer here to reuse its achieved_amount logic
#             from accounts.serializers.monthly_target_serializer import MonthlyTargetSerializer
#             total_dec = Decimal('0')
#             for mt in mt_qs:
#                 try:
#                     ser = MonthlyTargetSerializer(mt)
#                     achieved = ser.get_achieved_amount(mt)
#                     total_dec += Decimal(str(achieved))
#                 except Exception:
#                     continue
#             total_actual_revenue = float(total_dec)
#     except Exception:
#         # Fallback to previous per-user sum if anything fails
#         total_actual_revenue = sum([u['actual_revenue'] for u in revenue_vs_user]) if revenue_vs_user else 0

#     # Opportunity chart 1 — count and total value per status (ALL active statuses)
#     all_opp_statuses = list(Lead_Status.objects.filter(is_active=True).values_list('name', flat=True))
#     opp_status_actual = {
#         row['status_name']: {'count': row['count'], 'total_value': float(row['total_value'] or 0)}
#         for row in all_opps_q.values(status_name=F('opportunity_status__name')).annotate(count=Count('id'), total_value=Sum('opportunity_value'))
#     }
#     opportunity_status_chart = [
#         {
#             'status': s,
#             'count': opp_status_actual.get(s, {}).get('count', 0),
#             'total_value': opp_status_actual.get(s, {}).get('total_value', 0.0),
#         }
#         for s in all_opp_statuses
#     ]

#     # Opportunity chart 2 — conversion rate by source (ALL active lead sources)
#     opp_src_actual = {
#         row['source_name']: row['total']
#         for row in all_opps_q.values(source_name=F('lead__lead_source__source')).annotate(total=Count('id'))
#     }
#     opp_conv_by_source = []
#     for source_name in all_lead_sources:
#         total = opp_src_actual.get(source_name, 0)
#         won_count = all_opps_q.filter(
#             lead__lead_source__source=source_name,
#             opportunity_status_id__in=won_ids,
#         ).count()
#         rate = (won_count / total * 100) if total else 0
#         opp_conv_by_source.append({
#             'source': source_name,
#             'total': total,
#             'won': won_count,
#             'conversion_rate': round(rate, 2),
#         })

#     # Common cards and charts (always included)
#     common_cards = {
#         'total_actual_revenue': float(total_actual_revenue),
#         'total_tasks': total_tasks,
#         'overdue_tasks': overdue_tasks,
#         'overdue_rate': overdue_rate,
#         'active_targets': active_targets,
#         'team_avg_achievement': team_avg_achievement,
#     }
#     common_charts = {
#         'revenue_target_vs_actual_by_user': revenue_vs_user,
#     }

#     opportunity_mode = request.query_params.get('opportunity', '').strip().lower() in ('true', '1', 'yes')

#     if opportunity_mode:
#         data = {
#             'cards': {
#                 **common_cards,
#                 'total_opportunities': total_opportunities,
#                 'total_contacts': total_contacts,
#                 'contacts_without_lead': contacts_without_lead,
#                 'contacts_with_lead': contacts_with_lead,
#                 'converted_opportunities': converted_opps,
#                 'opportunity_conversion_rate': round(opportunity_conversion_rate, 2),
#             },
#             'charts': {
#                 **common_charts,
#                 'opportunity_status': opportunity_status_chart,
#                 'opportunity_conversion_rate_by_source': opp_conv_by_source,   
#             # 'contacts_chart': {
#                 'contact_status_distribution': contact_status_distribution,
#                 'source_distribution': all_contacts_source_dist,
#                 'task_type_distribution': task_type_distribution,
#             # },            
#             },

#         }
#     else:
#         data = {
#             'cards': {
#                 **common_cards,
#                 'total_contacts': total_contacts,
#                 'total_leads': total_leads,
#                 'contacts_without_lead': contacts_without_lead,
#                 'contacts_with_lead': contacts_with_lead,
#                 # 'converted_leads': converted_leads,
#                 'lead_conversion_rate': lead_conversion_rate,
#             },
#             'charts': {
#                 **common_charts,
#                 'lead_distribution_status': lead_distribution_status,
#                 'conversion_rate_by_source': conv_by_source,
#             # 'contacts_chart': {
#                 'contact_status_distribution': contact_status_distribution,
#                 'source_distribution': all_contacts_source_dist,
#                 'task_type_distribution': task_type_distribution,
#             # }               
#             },

#         }

#     return Response(data)


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
                # Last 6 complete calendar months (1st of month, 6 months back → end of last month)
                first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                start = first_of_this_month - relativedelta(months=6)
                end = first_of_this_month
            elif preset in ('1month', '1_month', '1-month', '1m', '1', 'current_month', 'this_month'):
                # Current month: from 1st of this month to end of this month
                start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end = (start + relativedelta(months=1))
            elif preset in ('last_month', 'lastmonth', 'last month', 'last-month'):
                # Previous month: from 1st to last day of last month
                first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                start = first_of_this_month - relativedelta(months=1)
                end = first_of_this_month
            elif preset in ('7days', '7_days', '7-days', '7d', '7'):
                start = now - timedelta(days=7)
            elif preset in ('1year', '1_year', 'last_year', '12months', '12_months', '1y'):
                # Last 12 complete calendar months
                first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                start = first_of_this_month - relativedelta(months=12)
                end = first_of_this_month
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

        # Ensure timezone-aware datetimes for safe comparisons with timezone.now()
        if timezone.is_naive(start):
            start = timezone.make_aware(start)
        if timezone.is_naive(end):
            end = timezone.make_aware(end)
    except Exception:
        return Response({"error": "Invalid date format. Use YYYY-MM-DD or valid preset."}, status=400)

    # Optional user filter
    user_id = request.query_params.get('user_id') or request.query_params.get('user')
    is_team = request.query_params.get('team', '').lower() == 'true'
    user_obj = None
    is_admin = False
    is_bdm = False
    team_member_ids = []
    if user_id:
        try:
            user_obj = User.objects.filter(id=int(user_id)).first()
            if user_obj:
                is_admin = user_obj.groups.filter(name__iexact="Admin").exists()
                is_bdm = user_obj.groups.filter(name__iexact="BDM").exists()
                if is_bdm:
                    from accounts.models import Teams
                    user_team = Teams.objects.filter(bdm_user=user_obj).first()
                    if user_team:
                        team_member_ids = list(user_team.bde_user.values_list("id", flat=True))
            else:
                user_id = None
        except Exception:
            user_id = None
            user_obj = None

    # Cards
    leads_q = Lead.objects.filter(is_active=True, created_on__gte=start, created_on__lt=end)
    if user_obj:
        if is_admin:
            if is_team:
                leads_q = leads_q.exclude(Q(created_by=user_obj) | Q(assigned_to=user_obj))
            else:
                leads_q = leads_q.filter(Q(created_by=user_obj) | Q(assigned_to=user_obj))
        elif is_bdm:
            if is_team:
                leads_q = leads_q.filter(Q(created_by__in=team_member_ids) | Q(assigned_to__in=team_member_ids))
            else:
                leads_q = leads_q.filter(Q(created_by=user_obj) | Q(assigned_to=user_obj))
        else:
            leads_q = leads_q.filter(Q(assigned_to=user_obj) | Q(created_by=user_obj))
    leads_q = leads_q.distinct()
    total_leads = leads_q.count()

    converted_leads_q = leads_q.filter(lead_status__name__iexact='converted')
    converted_leads = converted_leads_q.count()

    lead_conversion_rate = (converted_leads / total_leads * 100) if total_leads else 0

    # Total actual revenue from won/converted opportunities
    won_ids = [34]  # 'Deal Won' status ID
    opportunities_q = Opportunity.objects.filter(is_active=True, closing_date__gte=start.date(), closing_date__lt=end.date(), opportunity_status_id__in=won_ids)
    if user_obj:
        if is_admin:
            if is_team:
                opportunities_q = opportunities_q.exclude(Q(lead__created_by=user_obj) | Q(lead__assigned_to=user_obj))
            else:
                opportunities_q = opportunities_q.filter(Q(lead__created_by=user_obj) | Q(lead__assigned_to=user_obj))
        elif is_bdm:
            if is_team:
                opportunities_q = opportunities_q.filter(Q(lead__assigned_to__in=team_member_ids) | Q(lead__created_by__in=team_member_ids))
            else:
                opportunities_q = opportunities_q.filter(Q(lead__assigned_to=user_obj) | Q(lead__created_by=user_obj))
        else:
            opportunities_q = opportunities_q.filter(Q(lead__assigned_to=user_obj) | Q(lead__created_by=user_obj))
    
    if user_obj and not is_team:
        total_actual_revenue = opportunities_q.aggregate(total=Sum('opportunity_value'))['total'] or 0
    else:
        # Company-wide total
        total_actual_revenue = opportunities_q.aggregate(total=Sum('opportunity_value'))['total'] or 0

    # Total opportunities (all statuses) — no is_active filter, matches opportunity list API
    all_opps_q = Opportunity.objects.filter(is_active=True, created_on__gte=start, created_on__lt=end)
    if user_obj:
        if is_admin:
            if is_team:
                all_opps_q = all_opps_q.exclude(Q(lead__created_by=user_obj) | Q(lead__assigned_to=user_obj))
            else:
                all_opps_q = all_opps_q.filter(Q(lead__created_by=user_obj) | Q(lead__assigned_to=user_obj))
        elif is_bdm:
            if is_team:
                all_opps_q = all_opps_q.filter(Q(lead__assigned_to__in=team_member_ids) | Q(lead__created_by__in=team_member_ids))
            else:
                all_opps_q = all_opps_q.filter(Q(lead__assigned_to=user_obj) | Q(lead__created_by=user_obj))
        else:
            all_opps_q = all_opps_q.filter(Q(lead__assigned_to=user_obj) | Q(lead__created_by=user_obj))
    total_opportunities = all_opps_q.count()

    # Converted (won) opportunities and conversion rate
    converted_opps = all_opps_q.filter(opportunity_status_id__in=won_ids).count()
    opportunity_conversion_rate = (converted_opps / total_opportunities * 100) if total_opportunities else 0

    # Tasks scoped to the requested date range
    tasks_q = Task.objects.filter(is_active=True, task_date_time__gte=start, task_date_time__lt=end)
    if user_obj:
        if is_admin:
            if is_team:
                tasks_q = tasks_q.exclude(Q(created_by=user_obj) | Q(task_task_assignments__assigned_to=user_obj))
            else:
                tasks_q = tasks_q.filter(Q(created_by=user_obj) | Q(task_task_assignments__assigned_to=user_obj))
        elif is_bdm:
            if is_team:
                tasks_q = tasks_q.filter(created_by__in=team_member_ids)
            else:
                tasks_q = tasks_q.filter(Q(task_task_assignments__assigned_to=user_obj.id) | Q(created_by=user_obj))
        else:
            tasks_q = tasks_q.filter(Q(task_task_assignments__assigned_to=user_obj.id) | Q(created_by=user_obj))
    tasks_q = tasks_q.distinct()
    total_tasks = tasks_q.count()

    now = timezone.now()
    overdue_q = tasks_q.filter(task_date_time__lt=now, is_active=True)
    overdue_tasks = overdue_q.count()
    overdue_rate = (overdue_tasks / total_tasks * 100) if total_tasks else 0

    # Active targets (count of monthly targets + active user targets within range)
    mt_q = MonthlyTarget.objects.filter(created_at__gte=start, created_at__lt=end)
    ut_q = UserTarget.objects.filter(created_at__gte=start, created_at__lt=end, is_active=True)
    if user_id:
        if is_team:
            mt_q = mt_q.exclude(user_id=user_id)
            ut_q = ut_q.exclude(user_id=user_id)
        else:
            mt_q = mt_q.filter(user_id=user_id)
            ut_q = ut_q.filter(user_id=user_id)
    monthly_targets_count = mt_q.count()
    user_targets_count = ut_q.count()
    active_targets = monthly_targets_count + user_targets_count

    # Users to exclude from all responses
    EXCLUDED_USERNAMES = {'root', 'support@irepute.in'}

    # build months list for range (robust) and exclude future months (only up to current month)
    def build_months_list(start_dt, end_dt):
        s = start_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_inclusive = (end_dt - timedelta(days=1))
        e = last_inclusive.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        months_list_local = []
        cur = s
        while cur <= e:
            months_list_local.append((cur.year, cur.month))
            cur = cur + relativedelta(months=1)
        return months_list_local

    months_list = build_months_list(start, end)
    now = timezone.now()
    current_month_tuple = (now.year, now.month)
    months_list = [m for m in months_list if m <= current_month_tuple]
    months = set(months_list)

    def display_name(u):
        """Return first name if set, otherwise the username local part (before @)."""
        if u.first_name.strip():
            return u.first_name.strip()
        username = u.username
        if '@' in username:
            username = username.split('@')[0]
        return username

    def get_cumulative_target(u, from_dt, cap_dt):
        """Returns the cumulative MT value up to cap_dt."""
        cap_year, cap_month = cap_dt.year, cap_dt.month
        mt_end = (
            MonthlyTarget.objects.filter(user=u, year__lt=cap_year) |
            MonthlyTarget.objects.filter(user=u, year=cap_year, month__lte=cap_month)
        ).order_by('-year', '-month').first()
        if not mt_end:
            return None
        return float(mt_end.target_amount)

    has_date_filter = bool(request.query_params.get('start_date') or
                           request.query_params.get('end_date') or
                           request.query_params.get('preset') or
                           request.query_params.get('period'))

    # Helper: merge actual counts with full master list, defaulting missing entries to 0
    from lead.models import Lead_Status
    from accounts.models import Lead_Source, Contact_Status, Stage as OppStage

    # Lead distribution by status — show ALL active lead statuses
    all_lead_statuses = list(Lead_Status.objects.filter(is_active=True).values_list('name', flat=True))
    lead_dist_actual = {
        d['status_name']: d['count']
        for d in leads_q.values(status_name=F('lead_status__name')).annotate(count=Count('id'))
    }
    lead_distribution_status = [
        {'status': s, 'count': lead_dist_actual.get(s, 0)}
        for s in all_lead_statuses
    ]
    # Contacts (used by sources and contact charts)
    contacts_q = Contact.objects.filter(is_active=True, created_on__gte=start, created_on__lt=end)
    if user_obj:
        if is_admin:
            if is_team:
                contacts_q = contacts_q.exclude(Q(assigned_to=user_obj) | Q(created_by=user_obj))
            else:
                contacts_q = contacts_q.filter(Q(assigned_to=user_obj) | Q(created_by=user_obj))
        elif is_bdm:
            if is_team:
                contacts_q = contacts_q.filter(Q(assigned_to__in=team_member_ids) | Q(created_by__in=team_member_ids))
            else:
                contacts_q = contacts_q.filter(Q(assigned_to=user_obj) | Q(created_by=user_obj))
        else:
            contacts_q = contacts_q.filter(Q(assigned_to=user_obj) | Q(created_by=user_obj))
    contact_dist = contacts_q.values(status_name=F('status__status')).annotate(count=Count('id')).order_by('-count')
    # Show ALL active contact statuses, with 0 for missing ones
    all_contact_statuses = list(Contact_Status.objects.filter(is_active=True).values_list('status', flat=True))
    contact_dist_actual = {d['status_name']: d['count'] for d in contact_dist}
    contact_status_distribution = [
        {'status': s, 'count': contact_dist_actual.get(s, 0)}
        for s in all_contact_statuses
    ]
    total_contacts = contacts_q.count()
    contacts_without_lead = contacts_q.filter(lead__isnull=True, is_archive=False).count()
    contacts_with_lead = contacts_q.filter(lead__isnull=False).count()

    # Lead-source distribution — show ALL active lead sources, with 0 for missing ones
    all_lead_sources = list(Lead_Source.objects.filter(is_active=True).values_list('source', flat=True))
    sources_actual = {
        s['source_name']: s['total']
        for s in leads_q.values(source_name=F('lead_source__source')).annotate(total=Count('id'))
    }
    conv_by_source = []
    for source_name in all_lead_sources:
        total = sources_actual.get(source_name, 0)
        converted = leads_q.filter(lead_source__source=source_name, lead_status__name__iexact='converted').count()
        rate = (converted / total * 100) if total else 0
        conv_by_source.append({'source': source_name, 'total': total, 'converted': converted, 'conversion_rate': round(rate, 2)})

    # All contacts source distribution — show ALL active lead sources
    all_contacts_src_actual = {
        s['source_name']: s['count']
        for s in contacts_q.values(source_name=F('lead_source__source')).annotate(count=Count('id'))
    }
    all_contacts_source_dist = [
        {'source': s, 'count': all_contacts_src_actual.get(s, 0)}
        for s in all_lead_sources
    ]

    # Task type distribution (counts per task_type) for charts
    task_types_q = tasks_q.values(type_name=F('task_type')).annotate(count=Count('id')).order_by('-count')
    task_type_distribution = [{'task_type': t['type_name'] or 'Unknown', 'count': t['count']} for t in task_types_q]

    # (contacts_q was defined earlier)
    total_contacts = contacts_q.count()

    users_with_targets = User.objects.exclude(username__in=EXCLUDED_USERNAMES)
    if user_id:
        if is_team:
            users_with_targets = users_with_targets.exclude(id=user_id)
        else:
            users_with_targets = users_with_targets.filter(id=user_id)
    revenue_vs_user = []
    now_for_target = timezone.now()

    # Financial year = Apr to Mar
    # Current FY: Apr 2026 – Mar 2027
    now_fy = timezone.now()
    if now_fy.month >= 4:
        fy_start_year = now_fy.year
    else:
        fy_start_year = now_fy.year - 1
    fy_months = []
    for i in range(12):
        m = ((3 + i) % 12) + 1   # Apr=4 … Mar=3
        y = fy_start_year if m >= 4 else fy_start_year + 1
        fy_months.append((y, m))

    # When user_id is given and not team → show month-by-month breakdown.
    # With date filter: split across months in the given range.
    # Without date filter: split across the current financial year (Apr–Mar).
    user_fy_mode = bool(user_id) and not is_team

    if user_fy_mode:
        if has_date_filter or preset:
            # Build month list from the requested date range
            # Guard: if start is epoch fallback, use current month only
            effective_start = start
            if effective_start.year < 2000:
                effective_start = (end - relativedelta(months=1)).replace(day=1)
            range_months_list = []
            cy, cm = effective_start.year, effective_start.month
            cap_ym = ((end - relativedelta(days=1)).year, (end - relativedelta(days=1)).month)
            while (cy, cm) <= cap_ym:
                range_months_list.append((cy, cm))
                cm += 1
                if cm > 12:
                    cm = 1
                    cy += 1
        else:
            # No filter: use current financial year Apr–Mar
            range_months_list = fy_months

        for u in users_with_targets:
            monthly_data = []
            # Determine from which month this user became inactive (once, outside the month loop)
            if u.is_active:
                inactive_from = None
            else:
                from accounts.models import UserActiveHistory as _UAH
                last_inactive = _UAH.objects.filter(user=u, is_active=False).order_by('-changed_at').first()
                inactive_from = (last_inactive.changed_at.year, last_inactive.changed_at.month) if last_inactive else None

            # Skip user if they were already inactive at the start of the requested range
            if has_date_filter and inactive_from and inactive_from <= (start.year, start.month):
                continue

            for (yr, mo) in range_months_list:
                month_start = timezone.make_aware(datetime(yr, mo, 1))
                month_end = timezone.make_aware(datetime(yr + 1, 1, 1) if mo == 12 else datetime(yr, mo + 1, 1))
                # Actual: same weighted logic as AnnualTargetAnalyticsViewSet._sum_achieved
                month_start_d = month_start.date()
                month_end_d = (month_end - timedelta(days=1)).date()
                qs = Opportunity.objects.filter(
                    opportunity_status_id=34,
                    is_active=True,
                    closing_date__range=(month_start_d, month_end_d),
                )
                actual_mo = Decimal('0.00')
                for condition, weight in [
                    (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
                    (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
                    (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), Decimal('0.5')),
                    (~Q(lead__created_by=u) & Q(lead__assigned_to=u), Decimal('0.5')),
                ]:
                    val = qs.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
                    actual_mo += Decimal(str(val)) * Decimal(str(weight))
                actual_mo = float(actual_mo)
                # # Actual: won opps by lead.created_by closed in this month
                # actual_mo = float(Opportunity.objects.filter(
                #     is_active=True,
                #     closing_date__gte=month_start.date(),
                #     closing_date__lt=month_end.date(),
                #     opportunity_status_id=34,
                #     lead__created_by=u,
                # ).aggregate(total=Sum('opportunity_value'))['total'] or 0)

                # Target: 0 if user became inactive this month or earlier, else use MT
                mt_this = MonthlyTarget.objects.filter(user=u, year=yr, month=mo).first()
                if inactive_from and (yr, mo) >= inactive_from:
                    target_mo = 0.0
                elif mt_this:
                    target_mo = float(mt_this.target_amount)
                else:
                    ut = UserTarget.objects.filter(user=u, is_active=True).first()
                    target_mo = float(ut.target) / 12.0 if ut else 0.0

                achievement_mo = (actual_mo / target_mo * 100) if target_mo > 0 else 0.0
                monthly_data.append({
                    'month': f"{yr}-{mo:02d}",
                    'target_amount': round(target_mo, 2),
                    'actual_revenue': round(actual_mo, 2),
                    'achievement_percentage': round(achievement_mo, 2),
                })

            revenue_vs_user.append({
                'username': display_name(u),
                'monthly_breakdown': monthly_data,
            })

    else:
        for u in users_with_targets:
            # Only skip inactive users when an explicit date filter is passed AND
            # the user was already inactive before the start of that range
            if has_date_filter and not u.is_active:
                from accounts.models import UserActiveHistory as _UAH
                _last_inactive = _UAH.objects.filter(user=u, is_active=False).order_by('-changed_at').first()
                if _last_inactive:
                    _inactive_ym = (_last_inactive.changed_at.year, _last_inactive.changed_at.month)
                    _range_start_ym = (start.year, start.month)
                    # Skip if user went inactive on or before the start of the range
                    if _inactive_ym <= _range_start_ym:
                        continue

            # Weighted revenue calculation aligned with targets
            actual = 0
            opps_in_range_q = Opportunity.objects.filter(
                is_active=True,
                closing_date__gte=start.date(),
                closing_date__lt=end.date(),
                opportunity_status_id=34
            )
            # Exact same 4-filter logic as MonthlyTargetSerializer.get_achieved_amount
            filters_with_weights = [
                (Q(lead__created_by=u) & Q(lead__assigned_to=u), 1),
                (Q(lead__created_by=u) & Q(lead__assigned_to__isnull=True), 1),
                (Q(lead__created_by=u) & ~Q(lead__assigned_to=u) & Q(lead__assigned_to__isnull=False), 0.5),
                (~Q(lead__created_by=u) & Q(lead__assigned_to=u), 0.5),
            ]
            for condition, weight in filters_with_weights:
                val = opps_in_range_q.filter(condition).aggregate(total=Sum('opportunity_value'))['total'] or 0
                actual += float(val) * weight

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
                # If user went inactive within the range, cap target at month before inactive
                if not u.is_active:
                    from accounts.models import UserActiveHistory as _UAH3
                    _li2 = _UAH3.objects.filter(user=u, is_active=False).order_by('-changed_at').first()
                    if _li2:
                        _inactive_start = datetime(_li2.changed_at.year, _li2.changed_at.month, 1, tzinfo=range_cap.tzinfo)
                        _capped = _inactive_start - relativedelta(days=1)
                        # Only apply cap if user went inactive before the range end
                        if _capped < range_cap:
                            range_cap = _capped
            else:
                # No filter: full range from user's first MT up to now
                range_from = start.tzinfo and datetime(user_start[0], user_start[1], 1, tzinfo=start.tzinfo) or timezone.make_aware(datetime(user_start[0], user_start[1], 1))
                range_cap = now_for_target
                # If user is inactive, cap target at the month before they went inactive
                if not u.is_active:
                    from accounts.models import UserActiveHistory as _UAH2
                    _li = _UAH2.objects.filter(user=u, is_active=False).order_by('-changed_at').first()
                    if _li:
                        # Cap = last day of month before inactive month
                        _inactive_month_start = datetime(_li.changed_at.year, _li.changed_at.month, 1, tzinfo=now_for_target.tzinfo)
                        range_cap = _inactive_month_start - relativedelta(days=1)

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

            achievement = (float(actual) / float(target_amount) * 100) if target_amount and float(target_amount) > 0 else 0
            revenue_vs_user.append({
                'username': display_name(u),
                'target_amount': float(target_amount),
                'actual_revenue': float(actual),
                'achievement_percentage': achievement,
                'target_breakdown': breakdown,
            })

    # Compute company-wide actual revenue as sum of achieved_amount from MonthlyTarget rows
    total_actual_revenue = 0
    try:
        if months:
            years = [y for y, m in months]
            months_vals = [m for y, m in months]
            mt_qs = MonthlyTarget.objects.filter(year__in=years, month__in=months_vals)
            if user_id:
                if is_team:
                    mt_qs = mt_qs.exclude(user_id=user_id)
                else:
                    mt_qs = mt_qs.filter(user_id=user_id)
            # Import serializer here to reuse its achieved_amount logic
            from accounts.serializers.monthly_target_serializer import MonthlyTargetSerializer
            total_dec = Decimal('0')
            for mt in mt_qs:
                try:
                    ser = MonthlyTargetSerializer(mt)
                    achieved = ser.get_achieved_amount(mt)
                    total_dec += Decimal(str(achieved))
                except Exception:
                    continue
            total_actual_revenue = float(total_dec)
    except Exception:
        # Fallback to previous per-user sum if anything fails
        total_actual_revenue = sum([u['actual_revenue'] for u in revenue_vs_user]) if revenue_vs_user else 0

    # team_avg_achievement = (total_actual_revenue / cumulative target at current month) * 100
    _now = timezone.now()
    _now_ym = (_now.year, _now.month)
    _team_target = 0.0
    for row in revenue_vs_user:
        if 'monthly_breakdown' in row:
            past = [mo for mo in row['monthly_breakdown']
                    if mo.get('target_amount', 0) > 0
                    and tuple(int(x) for x in mo['month'].split('-')) <= _now_ym]
            if past:
                _team_target += past[-1]['target_amount']
        else:
            _team_target += row.get('target_amount', 0)
    team_avg_achievement = (float(total_actual_revenue) / _team_target * 100) if _team_target > 0 else 0

    # Opportunity chart 1 — count and total value per status (ALL active statuses)
    all_opp_statuses = list(Lead_Status.objects.filter(is_active=True).values_list('name', flat=True))
    opp_status_actual = {
        row['status_name']: {'count': row['count'], 'total_value': float(row['total_value'] or 0)}
        for row in all_opps_q.values(status_name=F('opportunity_status__name')).annotate(count=Count('id'), total_value=Sum('opportunity_value'))
    }
    opportunity_status_chart = [
        {
            'status': s,
            'count': opp_status_actual.get(s, {}).get('count', 0),
            'total_value': opp_status_actual.get(s, {}).get('total_value', 0.0),
        }
        for s in all_opp_statuses
    ]

    # Opportunity chart 2 — conversion rate by source (ALL active lead sources)
    opp_src_actual = {
        row['source_name']: row['total']
        for row in all_opps_q.values(source_name=F('lead__lead_source__source')).annotate(total=Count('id'))
    }
    opp_conv_by_source = []
    for source_name in all_lead_sources:
        total = opp_src_actual.get(source_name, 0)
        won_count = all_opps_q.filter(
            lead__lead_source__source=source_name,
            opportunity_status_id__in=won_ids,
        ).count()
        rate = (won_count / total * 100) if total else 0
        opp_conv_by_source.append({
            'source': source_name,
            'total': total,
            'won': won_count,
            'conversion_rate': round(rate, 2),
        })

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
                'total_contacts': total_contacts,
                'contacts_without_lead': contacts_without_lead,
                'contacts_with_lead': contacts_with_lead,
                'converted_opportunities': converted_opps,
                'opportunity_conversion_rate': round(opportunity_conversion_rate, 2),
            },
            'charts': {
                **common_charts,
                'opportunity_status': opportunity_status_chart,
                'opportunity_conversion_rate_by_source': opp_conv_by_source,   
            # 'contacts_chart': {
                'contact_status_distribution': contact_status_distribution,
                'source_distribution': all_contacts_source_dist,
                'task_type_distribution': task_type_distribution,
            # },            
            },

        }
    else:
        data = {
            'cards': {
                **common_cards,
                'total_contacts': total_contacts,
                'total_leads': total_leads,
                'contacts_without_lead': contacts_without_lead,
                'contacts_with_lead': contacts_with_lead,
                # 'converted_leads': converted_leads,
                'lead_conversion_rate': lead_conversion_rate,
            },
            'charts': {
                **common_charts,
                'lead_distribution_status': lead_distribution_status,
                'conversion_rate_by_source': conv_by_source,
            # 'contacts_chart': {
                'contact_status_distribution': contact_status_distribution,
                'source_distribution': all_contacts_source_dist,
                'task_type_distribution': task_type_distribution,
            # }               
            },

        }

    return Response(data)