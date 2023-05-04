import django_filters
from products.models import Product

class ProductFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    total_price_min = django_filters.NumberFilter(field_name="total_price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lt")
    total_price_max = django_filters.NumberFilter(field_name="total_price", lookup_expr="lt")


    class Meta:
        model = Product
        fields = ('name', 'price',
                  'price_min', 'price_max',
                  'total_price_min', 'total_price_max',
                  'category__id', 'category__name',
        )