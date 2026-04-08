from rest_framework import serializers
from apps.properties.models import PropertiesPhotos
from apps.properties.services import upload_to_cloud, delete_from_cloud, generate_url

ALLOWED_FORMATS = ['image/jpeg', 'image/jpg', 'image/png']
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_PHOTOS = 20
MIN_PHOTOS = 1

class PropertiesUploadPhotosSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(write_only=True, allow_empty_file=False)

    def validate_image(self, image):
        if image.content_type not in ALLOWED_FORMATS:
            raise serializers.ValidationError(
            "Invalid format. Only JPG, JPEG and PNG are accepted."
            )

        if image.size > MAX_SIZE_BYTES:
            raise serializers.ValidationError(
            f"Maximum size per photo is 5MB. This file has {image.size // (1024*1024)}MB."
            )

        return image
    
    def validate(self, data):
        property_obj = self.context.get('property')
        if property_obj:
            current_count = property_obj.photos.count()
            if current_count >= MAX_PHOTOS:
                raise serializers.ValidationError(
                f"A property can have a maximum of {MAX_PHOTOS} photos. This property already has {current_count}."
                )
        return data

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
        fields = ['id', 'image', 'order']

class PropertiesPhotosSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return generate_url(obj.r2_key)

    class Meta:
        model = PropertiesPhotos
        fields = ['id', 'url', 'order']

