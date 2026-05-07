from django.shortcuts import get_object_or_404

from apps.properties.models import Properties
from apps.users.models import SearchPreference, User


class UserRepository:
    @staticmethod
    def create_user(*, email, name, user_type, password):
        return User.objects.create_user(
            email=email,
            name=name,
            user_type=user_type,
            password=password,
        )

    @staticmethod
    def email_exists(email):
        return User.objects.filter(email=email).exists()

    @staticmethod
    def save_user(user):
        user.save()
        return user


class SearchPreferenceRepository:
    @staticmethod
    def upsert_for_user(user, preferences_data):
        SearchPreference.objects.update_or_create(user=user, defaults=preferences_data)


class FavoriteRepository:
    @staticmethod
    def list_favorites(user):
        return user.favorites.all()

    @staticmethod
    def get_property_or_404(property_id):
        return get_object_or_404(Properties, id=property_id)

    @staticmethod
    def add_favorite(user, property_obj):
        user.favorites.add(property_obj)

    @staticmethod
    def remove_favorite(user, property_obj):
        user.favorites.remove(property_obj)
