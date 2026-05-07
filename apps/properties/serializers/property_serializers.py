from rest_framework import serializers
from apps.properties.models import Condo, Properties, Rooms, RoomsExtras, NearbyPlaces
from apps.properties.validators import validate_positive_number, validate_required_field
from apps.properties.serializers.photo_serializers import PropertiesPhotosSerializer
from apps.properties.use_cases import PropertyUseCase, ReviewUseCase


class RoomsExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomsExtras
        exclude = ["id"]

class CondoSerializer(serializers.ModelSerializer):

    def validate_name(self, value):
        return validate_required_field(value, "name")

    class Meta:
        model = Condo
        exclude = ["id"]

class RoomsSerializer(serializers.ModelSerializer):
    def validate_bedrooms(self, value):
        return validate_positive_number(value, "bedrooms")

    def validate_bathrooms(self, value):
        return validate_positive_number(value, "bathrooms")

    def validate_parking_spots(self, value):
        return validate_positive_number(value, "parking spots")

    class Meta:
        model = Rooms
        exclude = ["id"]
        extra_kwargs = {
            'bedrooms': {'required': False},
            'bathrooms': {'required': False},
            'parking_spots': {'required': False},
        }

class NearbyPlacesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NearbyPlaces
        fields = ["name", "category", "distance_meters", "rating"]

class PropertiesReadSerializer(serializers.ModelSerializer):
    rooms = RoomsSerializer()
    condo = CondoSerializer()
    rooms_extras = RoomsExtrasSerializer()
    images = PropertiesPhotosSerializer(many=True, read_only=True, source="photos")
    nearby_places = NearbyPlacesSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source="owner.name", read_only=True)
    
    def get_average_rating(self, obj):
        if hasattr(obj, "average_rating"):
            return obj.average_rating
        return ReviewUseCase.get_average_rating(obj)

    class Meta:
        model = Properties
        exclude = ["embedding"]


class PropertiesWriteSerializer(serializers.ModelSerializer):
    rooms = RoomsSerializer()
    condo = CondoSerializer(required=False, allow_null=True)
    rooms_extras = RoomsExtrasSerializer()

    def create(self, validated_data):
        return PropertyUseCase.create_property(validated_data)

    def update(self, instance, validated_data):
        return PropertyUseCase.update_property(instance, validated_data)

    def validate(self, data):
        if data.get("type") == "A" and not data.get("floor_number"):
            raise serializers.ValidationError("A floor number for an apartment is necessary")
        return data

    def validate_area(self, value):
        return validate_positive_number(value, "area")
    
    def validate_floors(self, value):
        return validate_positive_number(value, "floors")
    
    def validate_floor_number(self, value):
        return validate_positive_number(value, "floor number")

    def validate_price(self, value):
        return validate_positive_number(value, "price")
    
    def validate_address(self, value):
        return validate_required_field(value, "address")
    
    def validate_neighborhood(self, value):
        return validate_required_field(value, "neighborhood")
    
    def validate_city(self, value):
        return validate_required_field(value, "city")

    class Meta:
        model = Properties
        exclude = ["embedding"]
        read_only_fields = ["id", "owner"]
