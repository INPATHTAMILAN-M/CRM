import django_filters
from ..models import Note

class NoteFilter(django_filters.FilterSet):
    opportunity = django_filters.NumberFilter(field_name='opportunity__id', lookup_expr='exact')
    note_by = django_filters.NumberFilter(field_name='note_by__id', lookup_expr='exact')
    note_on = django_filters.DateFilter(field_name='note_on', lookup_expr='exact')
    lead = django_filters.NumberFilter(field_name='opportunity__lead__id', lookup_expr='exact')

    class Meta:
        model = Note
        fields = ['lead','opportunity', 'note_by', 'note_on']  # Fields you want to filter on
