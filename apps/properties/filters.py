import django_filters
from .models import Properties

class PropertiesFilters(django_filters.FilterSet):
    # price
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # Size
    min_area = django_filters.NumberFilter(field_name="area", lookup_expr="gte")
    max_area = django_filters.NumberFilter(field_name="area", lookup_expr="lte")


    # Localization
    neighborhood = django_filters.CharFilter(lookup_expr="icontains")
    city = django_filters.CharFilter(lookup_expr="icontains")

    #Rooms
    bedrooms = django_filters.BaseInFilter(field_name="rooms__bedrooms", lookup_expr="in")
    bathrooms = django_filters.BaseInFilter(field_name="rooms__bathrooms", lookup_expr="in")
    parking_spots = django_filters.BaseInFilter(field_name="rooms__parking_spots", lookup_expr="in")


    # Rooms Extras
    living_room = django_filters.BooleanFilter(field_name="rooms_extras__living_room")
    garden = django_filters.BooleanFilter(field_name="rooms_extras__garden")
    kitchen = django_filters.BooleanFilter(field_name="rooms_extras__kitchen")
    laundry_room = django_filters.BooleanFilter(field_name="rooms_extras__laundry_room")
    pool = django_filters.BooleanFilter(field_name="rooms_extras__pool")
    office = django_filters.BooleanFilter(field_name="rooms_extras__office")

    # Type
    type = django_filters.MultipleChoiceFilter(choices=Properties.TYPE_CHOICES)

    # Purpose
    property_purpose = django_filters.MultipleChoiceFilter(choices=Properties.PURPOSE_CHOICES)

    # Condo
    condo_name = django_filters.CharFilter(field_name="condo__name", lookup_expr="icontains")
    condo_gym = django_filters.BooleanFilter(field_name="condo__gym")
    condo_pool = django_filters.BooleanFilter(field_name="condo__pool")
    condo_court = django_filters.BooleanFilter(field_name="condo__court")
    condo_parks = django_filters.BooleanFilter(field_name="condo__parks")
    condo_party_spaces = django_filters.BooleanFilter(field_name="condo__party_spaces")
    condo_concierge = django_filters.BooleanFilter(field_name="condo__concierge")

    # Floors
    floors = django_filters.BaseInFilter(lookup_expr="in")
    floor_number = django_filters.BaseInFilter(lookup_expr="in")

    class Meta:
        model = Properties
        fields = []
