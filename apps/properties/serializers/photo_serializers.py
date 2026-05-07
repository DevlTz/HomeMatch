from rest_framework import serializers
from apps.properties.models import PropertiesPhotos
from apps.properties.services import generate_url
from apps.properties.use_cases import PhotoUseCase

class PropertiesUploadPhotosSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)

    def create(self, validated_data):
        property_obj = validated_data["property"]
        return PhotoUseCase.create_photo(property_obj=property_obj, validated_data=validated_data)

    def update(self, instance, validated_data):
        return PhotoUseCase.update_photo(instance, validated_data)


    class Meta:
        model = PropertiesPhotos
        fields = ['id', 'image', 'order']

class PropertiesPhotosSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return generate_url(obj.r2_key)


    class Meta:
        model = PropertiesPhotos
        fields = ['id', 'url']
