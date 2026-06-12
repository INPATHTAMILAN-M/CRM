from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, TextField
from django.db.models.functions import Cast
from lead.models import ApolloLead
from lead.serializers.apollo_lead_serializer import ApolloLeadSerializer


class ApolloLeadPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ApolloLeadViewSet(viewsets.ModelViewSet):
    queryset = ApolloLead.objects.all().order_by('-created_on')
    serializer_class = ApolloLeadSerializer
    lookup_field = 'pk'
    pagination_class = ApolloLeadPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['email_status', 'seniority', 'organization_name', 'country', 'city', 'contact']
    search_fields = ['first_name', 'last_name', 'full_name', 'email', 'organization_name', 'title',]
    ordering_fields = ['created_on', 'updated_on', 'first_name', 'email']

    def _extract_matches(self, payload):
        """Return a list of match dicts from possible wrappers in the payload."""
        if not isinstance(payload, dict):
            return []
        # Common shapes: {matches: [...]}, {data: {matches: [...] }}, or a single match dict
        if 'matches' in payload and isinstance(payload['matches'], list):
            return payload['matches']
        if 'data' in payload and isinstance(payload['data'], dict) and 'matches' in payload['data'] and isinstance(payload['data']['matches'], list):
            return payload['data']['matches']
        # If payload itself looks like a single match (has an id)
        if 'id' in payload:
            return [payload]
        return []

    def create(self, request, *args, **kwargs):
        payload = request.data
        matches = self._extract_matches(payload)
        if not matches:
            return Response({'detail': 'No matches found in payload'}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        updated = []

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
                # Additional fields from sample response
                'raw_json': item,
            }

            # Ensure we only pass model field names to update_or_create
            model_fields = {f.name for f in ApolloLead._meta.get_fields()}
            filtered_defaults = {k: v for k, v in defaults.items() if k in model_fields}

            # optional scalar extras remain inside raw_json for now
            obj, created_flag = ApolloLead.objects.update_or_create(external_id=external_id, defaults=filtered_defaults)
            if created_flag:
                created.append(obj.external_id)
            else:
                updated.append(obj.external_id)

        return Response({'created': created, 'updated': updated}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        """Override to include organization JSON text in search filtering.

        This annotates the `organization` JSONField as text and adds it to
        the search Q expression so `?search=<term>` will match phone numbers
        nested under `organization`.
        """
        qs = super().get_queryset()
        search = None
        if hasattr(self, 'request') and self.request:
            search = self.request.query_params.get('search')
        if not search:
            return qs

        # Cast JSONField to text so we can icontains-search nested values
        qs = qs.annotate(_org_text=Cast('organization', TextField()))

        return qs.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(full_name__icontains=search)
            | Q(email__icontains=search)
            | Q(organization_name__icontains=search)
            | Q(title__icontains=search)
            | Q(_org_text__icontains=search)
        )
