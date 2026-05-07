from apps.properties.validators import validate_rating, validate_comment_length
from rest_framework import serializers
from apps.properties.models import Reviews
from apps.properties.use_cases import ReviewUseCase

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
        
        if not property_id and self.instance:
            property_id = self.instance.property_id

        if not property_id:
            return data
        # Se estamos editando, self.instance não será Nones
        is_valid = ReviewUseCase.validate_unique_review(
            user=request.user,
            property_id=property_id,
            instance=self.instance,
        )
        if not is_valid:
            raise serializers.ValidationError("You have already reviewed this property.")
        return data