from django.db import models
from django.core.exceptions import ValidationError


class PhotoSubjectiveAttribute(models.Model):
    property = models.ForeignKey(
        "properties.Properties",
        on_delete=models.CASCADE,
        related_name="photo_subjective_attributes",
    )
    photo = models.ForeignKey(
        "properties.PropertiesPhotos",
        on_delete=models.CASCADE,
        related_name="subjective_attributes",
    )
    attribute_token = models.CharField(max_length=100)
    strength = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["attribute_token"]
        constraints = [
            models.UniqueConstraint(
                fields=["photo", "attribute_token"],
                name="ai_photo_subjective_attribute_unique_token_per_photo",
            )
        ]

    def clean(self):
        if self.photo_id and self.property_id and self.photo.property_id != self.property_id:
            raise ValidationError("Photo property and attribute property must refer to the same property.")

    def __str__(self):
        return f"{self.photo_id}:{self.attribute_token}={self.strength}"


class PropertySubjectiveAttribute(models.Model):
    property = models.ForeignKey(
        "properties.Properties",
        on_delete=models.CASCADE,
        related_name="subjective_attributes",
    )
    attribute_token = models.CharField(max_length=100)
    strength_mean = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["attribute_token"]
        constraints = [
            models.UniqueConstraint(
                fields=["property", "attribute_token"],
                name="ai_property_subjective_attribute_unique_token_per_property",
            )
        ]

    def __str__(self):
        return f"{self.property_id}:{self.attribute_token}={self.strength_mean}"
