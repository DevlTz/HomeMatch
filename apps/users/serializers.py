# apps/users/serializers.py
from rest_framework import serializers
from .models import User, SearchPreference
from .services import UserService

class SearchPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchPreference
        fields = ['property_type', 'min_price', 'max_price', 'city', 'neighborhood']

class UserSerializer(serializers.ModelSerializer):
    preferences = SearchPreferenceSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'age', 'gender', 'user_type', 'preferences']
        read_only_fields = ['user_type'] 

    def update(self, instance, validated_data):
        return UserService.update_user_profile(instance, validated_data)
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    user_type = serializers.ChoiceField(choices=User.UserType.choices, default=User.UserType.SEEKER)
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'user_type']

    def create(self, validated_data):
        return UserService.register_user(validated_data)

    def validate_email(self, value):
        email = UserService.normalize_and_validate_email(value)
        if email is None:
            raise serializers.ValidationError("This email is currently in use.")
        return email