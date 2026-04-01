from rest_framework import serializers

def validate_required_field(value, field):
        if not value:
            raise serializers.ValidationError(f"An {field} is necessary")
        return value

def validate_positive_number(value, field):
        if value < 0:
            raise serializers.ValidationError(f"Invalid {field}")
        return value

def validate_rating(value):
    if value < 1 or value > 5:
        raise serializers.ValidationError("Rating must be between 1 and 5.")
    return value

def validate_comment_length(value):
    if value and len(value) < 10:
        raise serializers.ValidationError("Comment must be at least 10 characters.")
    if value and len(value) > 1000:
        raise serializers.ValidationError("Comment must be less than 1000 characters.")
    return value