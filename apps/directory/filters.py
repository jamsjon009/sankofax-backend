import django_filters
from .models import Listing, Category


class ListingFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    city = django_filters.CharFilter(lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    price_range = django_filters.CharFilter()
    amenities = django_filters.CharFilter(method='filter_amenities')
    min_rating = django_filters.NumberFilter(field_name='avg_rating', lookup_expr='gte')
    featured = django_filters.BooleanFilter()

    class Meta:
        model = Listing
        fields = ['category', 'city', 'country', 'price_range', 'featured']

    def filter_amenities(self, queryset, name, value):
        slugs = [s.strip() for s in value.split(',') if s.strip()]
        for slug in slugs:
            queryset = queryset.filter(amenities__slug=slug)
        return queryset
