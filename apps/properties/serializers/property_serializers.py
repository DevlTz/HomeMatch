from unittest import result
from rest_framework import serializers
from apps.properties.models import Condo, Properties, Rooms, RoomsExtras
from apps.properties.validators import validate_positive_number, validate_required_field
from apps.properties.serializers.photo_serializers import PropertiesPhotosSerializer
from django.db.models import Avg


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


class PropertiesReadSerializer(serializers.ModelSerializer):
    rooms = RoomsSerializer()
    condo = CondoSerializer()
    rooms_extras = RoomsExtrasSerializer()
    images = PropertiesPhotosSerializer(many=True, read_only=True, source="photos")
    average_rating = serializers.SerializerMethodField()

    def get_average_rating(self, obj):
        result = obj.reviews.aggregate(Avg("rating"))
        return result["rating__avg"]

    class Meta:
        model = Properties
        exclude = ["embedding"]


class PropertiesWriteSerializer(serializers.ModelSerializer):
    rooms = RoomsSerializer()
    condo = CondoSerializer(required=False, allow_null=True)
    rooms_extras = RoomsExtrasSerializer()

    def create(self, validated_data):
        rooms_data = validated_data.pop('rooms')
        condo_data = validated_data.pop('condo', None)
        rooms_extras_data = validated_data.pop('rooms_extras')

        rooms, _ = Rooms.objects.get_or_create(**rooms_data)
        condo = None
        rooms_extras, _ = RoomsExtras.objects.get_or_create(**rooms_extras_data)

        if condo_data:
            condo, _ = Condo.objects.get_or_create(**condo_data)

        property = Properties.objects.create(
            rooms=rooms,
            rooms_extras=rooms_extras,
            condo=condo,
            **validated_data)

        return property

    def update(self, instance, validated_data):
        rooms_data = validated_data.pop('rooms', {})
        condo_data = validated_data.pop('condo', {})
        rooms_extras_data = validated_data.pop('rooms_extras', {})

        for attr, value in rooms_data.items():
            setattr(instance.rooms, attr, value)
        instance.rooms.save()

        for attr, value in condo_data.items():
            setattr(instance.condo, attr, value)
        instance.condo.save()

        for attr, value in rooms_extras_data.items():
            setattr(instance.rooms_extras, attr, value)
        instance.rooms_extras.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


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
        read_only_fields = ["id"]
