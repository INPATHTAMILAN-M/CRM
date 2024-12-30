import django_filters
from ..models import Contact, Lead


class ContactFilter(django_filters.FilterSet):
    lead = django_filters.ModelChoiceFilter(queryset=Lead.objects.all())
    is_active = django_filters.BooleanFilter(field_name='is_active', lookup_expr='exact')
    status = django_filters.NumberFilter(field_name='status__id', lookup_expr='icontains')  # assuming status is a ForeignKey to a model

    class Meta:
        model = Contact
        fields = '__all__'