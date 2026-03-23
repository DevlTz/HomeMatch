from rest_framework import serializers

def validate_required_field(value, field):
        if not value:
            raise serializers.ValidationError(f"An {field} is necessary")
        return value

def validate_positive_number(value, field):
        if value < 0:
            raise serializers.ValidationError(f"Invalid {field}")
        return value