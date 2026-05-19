from rest_framework import serializers

from apps.ai_analysis.schema import VALID_TOKENS


class NaturalSearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        max_length=500,
    )


class NaturalSearchCriteriaSerializer(serializers.Serializer):
    property_type = serializers.ChoiceField(
        choices=["A", "H"],
        allow_null=True,
        required=False,
    )
    min_price = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        allow_null=True,
        required=False,
    )
    max_price = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        allow_null=True,
        required=False,
    )
    city = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        max_length=100,
    )
    neighborhood = serializers.CharField(
        allow_blank=True,
        allow_null=True,
        required=False,
        max_length=100,
    )
    bedrooms = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    bathrooms = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    parking_spots = serializers.IntegerField(min_value=0, allow_null=True, required=False)
    desired_attributes = serializers.ListField(
        child=serializers.ChoiceField(choices=sorted(VALID_TOKENS)),
        required=False,
    )
    nearby_categories = serializers.ListField(
        child=serializers.ChoiceField(choices=["R", "G", "S", "H", "SM", "P"]),
        required=False,
    )

    def validate(self, attrs):
        min_price = attrs.get("min_price")
        max_price = attrs.get("max_price")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise serializers.ValidationError(
                {"max_price": "max_price must be greater than or equal to min_price."}
            )
        return attrs
