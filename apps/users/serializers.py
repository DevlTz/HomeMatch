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
        read_only_fields = ['user_type'] 

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
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'user_type']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            user_type=validated_data['user_type'],
            password=validated_data['password']
        )
        return user
    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is currently in use.")
        return email