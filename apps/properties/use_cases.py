from apps.properties.repositories import PhotoRepository, PropertyRepository, ReviewRepository


class PropertyUseCase:
    @staticmethod
    def create_property(validated_data):
        rooms_data = validated_data.pop("rooms")
        condo_data = validated_data.pop("condo", None)
        rooms_extras_data = validated_data.pop("rooms_extras")

        rooms, _ = PropertyRepository.get_or_create_rooms(rooms_data)
        rooms_extras, _ = PropertyRepository.get_or_create_rooms_extras(rooms_extras_data)
        condo = None
        if condo_data:
            condo, _ = PropertyRepository.get_or_create_condo(condo_data)

        return PropertyRepository.create_property(
            rooms=rooms,
            rooms_extras=rooms_extras,
            condo=condo,
            validated_data=validated_data,
        )

    @staticmethod
    def update_property(instance, validated_data):
        rooms_data = validated_data.pop("rooms", {})
        condo_data = validated_data.pop("condo", None)
        rooms_extras_data = validated_data.pop("rooms_extras", {})

        for attr, value in rooms_data.items():
            setattr(instance.rooms, attr, value)
        PropertyRepository.save_model(instance.rooms)

        if condo_data:
            condo_obj, _ = PropertyRepository.update_condo(instance.condo, condo_data)
            instance.condo = condo_obj

        for attr, value in rooms_extras_data.items():
            setattr(instance.rooms_extras, attr, value)
        PropertyRepository.save_model(instance.rooms_extras)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return PropertyRepository.save_model(instance)

    @staticmethod
    def delete_property(instance):
        rooms = instance.rooms
        rooms_extras = instance.rooms_extras
        instance.delete()

        if rooms and not rooms.properties.exists():
            rooms.delete()
        if rooms_extras and not rooms_extras.properties.exists():
            rooms_extras.delete()


class PhotoUseCase:
    @staticmethod
    def create_photo(*, property_obj, validated_data):
        image = validated_data["image"]
        order = validated_data["order"]
        return PhotoRepository.create_photo(property_obj=property_obj, image=image, order=order)

    @staticmethod
    def update_photo(instance, validated_data):
        new_image = validated_data.get("image")
        if new_image:
            return PhotoRepository.replace_photo_image(instance, new_image)
        return instance


class ReviewUseCase:
    @staticmethod
    def validate_unique_review(*, user, property_id, instance=None):
        return not ReviewRepository.user_has_review_for_property(
            user=user,
            property_id=property_id,
            instance=instance,
        )

    @staticmethod
    def get_reviews_for_property(property_id):
        return ReviewRepository.review_queryset_for_property(property_id)

    @staticmethod
    def get_average_rating(property_obj):
        return ReviewRepository.average_rating_for_property(property_obj)
