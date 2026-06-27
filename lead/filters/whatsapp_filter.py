from django_filters import rest_framework as filters
from django_filters.filters import OrderingFilter
from lead.models import Whatsapp

class WhatsappFilter(filters.FilterSet):
    ordering = OrderingFilter(
        fields=(
            ('id', 'id'),  
            ('name', 'name'),
            ('category', 'category'),
            ('created_on', 'created_on'),
        ),
        field_labels={
            'id': 'ID',
            'name': 'Name',
            'category': 'Category',
            'created_on': 'Created On',
        }
    )
    name = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Whatsapp
        fields = ['name', 'category']
