from apps.users.repositories import FavoriteRepository, SearchPreferenceRepository, UserRepository


class UserService:
    @staticmethod
    def register_user(validated_data):
        return UserRepository.create_user(
            email=validated_data["email"],
            name=validated_data["name"],
            user_type=validated_data["user_type"],
            password=validated_data["password"],
        )

    @staticmethod
    def update_user_profile(instance, validated_data):
        preferences_data = validated_data.pop("preferences", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        UserRepository.save_user(instance)

        if preferences_data:
            SearchPreferenceRepository.upsert_for_user(instance, preferences_data)

        return instance

    @staticmethod
    def normalize_and_validate_email(email):
        normalized_email = email.lower()
        if UserRepository.email_exists(normalized_email):
            return None
        return normalized_email


class FavoriteService:
    @staticmethod
    def list_user_favorites(user):
        return FavoriteRepository.list_favorites(user)

    @staticmethod
    def add_property_to_favorites(user, property_id):
        property_obj = FavoriteRepository.get_property_or_404(property_id)
        FavoriteRepository.add_favorite(user, property_obj)

    @staticmethod
    def remove_property_from_favorites(user, property_id):
        property_obj = FavoriteRepository.get_property_or_404(property_id)
        FavoriteRepository.remove_favorite(user, property_obj)
