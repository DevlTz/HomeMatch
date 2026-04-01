from apps.properties.validators import validate_rating, validate_comment_length
from rest_framework import serializers
from apps.properties.models import Reviews

class ReviewsSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.name", read_only=True)

    class Meta:
        model = Reviews
        fields = ['id', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user_name', 'created_at']

    def validate_rating(self, value):
        return validate_rating(value)

    def validate_comment(self, value):
        return validate_comment_length(value)

    def validate(self, data):
        request = self.context.get("request")
        property_id = self.context.get("property_id")
        if Reviews.objects.filter(user=request.user, property_id=property_id).exists():
            raise serializers.ValidationError("You have already reviewed this property.")
        return data