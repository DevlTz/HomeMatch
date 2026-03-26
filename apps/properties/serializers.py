from rest_framework import serializers
from .models import Properties, Rooms, Condo, RoomsExtras, PropertiesPhotos
from .validators import validate_positive_number, validate_required_field
from .services import upload_to_cloud, delete_from_cloud, generate_url

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

class PropertiesUploadPhotosSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)

    def create(self, validated_data):
        image = validated_data.pop('image')

        r2_key = upload_to_cloud(image)
        return PropertiesPhotos.objects.create(r2_key=r2_key, **validated_data)
    
    def update(self, instance, validated_data):
        new_image = validated_data.pop('image', None)

        if new_image:
            delete_from_cloud(instance.r2_key)
            instance.r2_key = upload_to_cloud(new_image)
            instance.save()

        return instance


    class Meta:
        model = PropertiesPhotos
        exclude = ['r2_key']

class PropertiesPhotosSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return generate_url(obj.r2_key)
    

    class Meta:
        model = PropertiesPhotos
        fields = ['id', 'url']

class PropertiesReadSerializer(serializers.ModelSerializer):
    rooms = RoomsSerializer()
    condo = CondoSerializer()
    rooms_extras = RoomsExtrasSerializer()
    images = PropertiesPhotosSerializer(many=True, read_only=True, source="photos")

    class Meta:
        model = Properties
        exclude = ["embedding"]


class PropertiesWriteSerializer(serializers.ModelSerializer):
    rooms = RoomsSerializer()
    condo = CondoSerializer()
    rooms_extras = RoomsExtrasSerializer()

    def create(self, validated_data):
        rooms_data = validated_data.pop('rooms')
        condo_data = validated_data.pop('condo')
        rooms_extras_data = validated_data.pop('rooms_extras')

        rooms = Rooms.objects.create(**rooms_data)
        condo = Condo.objects.create(**condo_data)
        rooms_extras = RoomsExtras.objects.create(**rooms_extras_data)

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
