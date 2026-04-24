from rest_framework import serializers
from apps.properties.models import PropertiesPhotos
from apps.properties.services import CloudService

class PropertiesUploadPhotosSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True)

    def create(self, validated_data):
        image = validated_data.pop('image')

        r2_key = CloudService.upload_to_cloud(image)
        return PropertiesPhotos.objects.create(r2_key=r2_key, **validated_data)

    def update(self, instance, validated_data):
        new_image = validated_data.pop('image', None)

        if new_image:
            CloudService.delete_from_cloud(instance.r2_key)
            instance.r2_key = CloudService.upload_to_cloud(new_image)
            instance.save()

        return instance


    class Meta:
        model = PropertiesPhotos
        fields = ['id', 'image', 'order']

class PropertiesPhotosSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return CloudService.generate_url(obj.r2_key)


    class Meta:
        model = PropertiesPhotos
        fields = ['id', 'url']
