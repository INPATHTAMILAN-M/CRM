# lead/views.py

import os
import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction

# local model for storing apollo responses
from lead.models import ApolloLead

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

        return Response({
            "success": True,
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