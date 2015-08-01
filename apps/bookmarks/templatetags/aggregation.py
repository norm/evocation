from datetime import timedelta
from django.template import Library

register = Library()


@register.filter
def by_year(queryset):
    return queryset.datetimes("date_added", "year", order="ASC")

@register.filter
def by_month(queryset, year):
    queryset = queryset.filter(
        date_added__gte=year,
        date_added__lte=year + timedelta(days=365),
    )
    return queryset.datetimes("date_added", "month", order="ASC")
