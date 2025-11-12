import django_filters
from django.contrib.auth import get_user_model
from ..models import Teams
from django.db.models import Q

User = get_user_model()


class TargetAnalyticsFilter(django_filters.FilterSet):
    """FilterSet used by the target analytics view.

    Notes:
    - Mirrors the parameters used by the view: `team` (bool), `team_id` (int),
      `company_name` (str) and `user_id` (int).
    - Uses Team membership (Teams.bdm_user / Teams.bde_user) to detect BDM/team members
      so behaviour matches the view logic.
    """

    team = django_filters.BooleanFilter(method="filter_team")
    company_name = django_filters.CharFilter(method="filter_company_name")

    class Meta:
        model = User
        fields = ["team","company_name"]


    def filter_team(self, queryset, name, value):
        """Handles ?team=true/false flag."""
        request = self.request
        user = request.user
        # consider a user an admin if they belong to the 'Admin' group
        is_admin = user.groups.filter(name__iexact="Admin").exists()
        is_bdm = user.groups.filter(name__iexact="BDM").exists()

        if is_admin:
            return queryset.exclude(created_by=user)

        if is_bdm:
            user_team = Teams.objects.filter(bdm_user=user).first()
            if not user_team:
                return queryset.none()
            if value:
                user_ids = list(user_team.bde_user.values_list("id", flat=True))
                return queryset.filter(id__in=user_ids)
            return queryset.filter(id=user.id)

        # non-admin, non-bdm -> only self
        return queryset.filter(id=user.id)

    def filter_company_name(self, queryset, name, value):
        """Filter users who have leads (created or owned) matching company name."""
        if not value:
            return queryset

        # Lead model stores company name in `name`. We check both related_name fields
        # used on Lead: `leads_created` (created_by) and `leads_owned` (lead_owner).
        return queryset.filter(
            Q(leads_created__name__icontains=value) | Q(leads_owned__name__icontains=value)
        ).distinct()
