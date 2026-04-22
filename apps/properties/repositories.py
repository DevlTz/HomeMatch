from django.db.models import Avg

from apps.properties.models import Condo, Properties, PropertiesPhotos, Reviews, Rooms, RoomsExtras
from apps.properties.services import delete_from_cloud, upload_to_cloud


class PropertyRepository:
    @staticmethod
    def get_or_create_rooms(rooms_data):
        return Rooms.objects.get_or_create(**rooms_data)

    @staticmethod
    def get_or_create_rooms_extras(rooms_extras_data):
        return RoomsExtras.objects.get_or_create(**rooms_extras_data)

    @staticmethod
    def get_or_create_condo(condo_data):
        return Condo.objects.get_or_create(**condo_data)

    @staticmethod
    def create_property(*, rooms, rooms_extras, condo, validated_data):
        return Properties.objects.create(
            rooms=rooms,
            rooms_extras=rooms_extras,
            condo=condo,
            **validated_data,
        )

    @staticmethod
    def update_condo(current_condo, condo_data):
        return Condo.objects.update_or_create(
            id=current_condo.id if current_condo else None,
            defaults=condo_data,
        )

    @staticmethod
    def save_model(instance):
        instance.save()
        return instance

    @staticmethod
    def list_properties_with_order():
        return Properties.objects.all().order_by("created_at")


class PhotoRepository:
    @staticmethod
    def create_photo(*, property_obj, image, order):
        r2_key = upload_to_cloud(image)
        return PropertiesPhotos.objects.create(property=property_obj, r2_key=r2_key, order=order)

    @staticmethod
    def replace_photo_image(instance, new_image):
        delete_from_cloud(instance.r2_key)
        instance.r2_key = upload_to_cloud(new_image)
        instance.save()
        return instance


class ReviewRepository:
    @staticmethod
    def user_has_review_for_property(*, user, property_id, instance=None):
        queryset = Reviews.objects.filter(user=user, property_id=property_id)
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        return queryset.exists()

    @staticmethod
    def review_queryset_for_property(property_id):
        return Reviews.objects.filter(property_id=property_id).order_by("-created_at")

    @staticmethod
    def average_rating_for_property(property_obj):
        result = property_obj.reviews.aggregate(Avg("rating"))
        return result["rating__avg"]
