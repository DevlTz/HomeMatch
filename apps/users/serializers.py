# apps/users/serializers.py
from rest_framework import serializers
from .models import User, SearchPreference

class SearchPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchPreference
        fields = ['property_type', 'min_price', 'max_price', 'city', 'neighborhood']

class UserSerializer(serializers.ModelSerializer):
    preferences = SearchPreferenceSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'age', 'gender', 'user_type', 'preferences']
        read_only_fields = ['email', 'user_type'] # Evitar que o user mude o próprio email/tipo na route

    def update(self, instance, validated_data):
        preferences_data = validated_data.pop('preferences', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if preferences_data:
            SearchPreference.objects.update_or_create(
                user=instance,
                defaults=preferences_data
            )
            
        return instance