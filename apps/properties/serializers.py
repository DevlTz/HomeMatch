from rest_framework import serializers
from .models import Properties, Rooms, Condo, RoomsExtras, PropertiesPhotos
from .validators import validate_positive_number, validate_required_field

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

class PropertiesPhotosSerializer(serializers.ModelSerializer):

    def get_url():
        pass

    class Meta:
        model = PropertiesPhotos
        exclude = ['r2_key']

class PropertiesSerializer(serializers.ModelSerializer):
    rooms = RoomsSerializer()
    condo = CondoSerializer()
    rooms_extras = RoomsExtrasSerializer()
    images = 

    def validate(self, data):
        if data.get("type") == "A" and not data.get("floor_number"):
            raise serializers.ValidationError("A floor number for an apartament is necessary")
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
        exclude = ["embedding", "photos_url", "created_at"]
