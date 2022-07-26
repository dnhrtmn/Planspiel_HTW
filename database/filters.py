import imp
from random import choices
import django_filters

from .models import OrderData
from .models import QualityData


class orderFilter(django_filters.FilterSet):

    CHOICES = (
        ('ascending', 'Aufsteigend'),
        ('descending', 'Absteigend')
    )

    ordering = django_filters.ChoiceFilter(
        label='Ordering', choices=CHOICES, method='filter_by_order')

    class Meta:
        model = OrderData
        fields = {
            'quantity': ['icontains'],
        }

    def filter_by_order(self, queryset, name, value):
        expression = 'orderDate' if value == 'ascending' else '-orderDate'
        return queryset.order_by(expression)


class qualityFilter(django_filters.FilterSet):
    class Meta:
        model = QualityData
        fields = ('orderNumber', 'failureStation')
