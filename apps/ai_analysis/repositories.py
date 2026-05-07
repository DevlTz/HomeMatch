from django.db import transaction
from django.db.models import Avg

from apps.ai_analysis.models import PhotoSubjectiveAttribute, PropertySubjectiveAttribute


class SubjectiveAttributeRepository:
    @staticmethod
    @transaction.atomic
    def replace_photo_attributes(photo, attributes):
        PhotoSubjectiveAttribute.objects.filter(photo=photo).delete()
        if attributes:
            PhotoSubjectiveAttribute.objects.bulk_create(
                [
                    PhotoSubjectiveAttribute(
                        property=photo.property,
                        photo=photo,
                        attribute_token=attribute["attribute_token"],
                        strength=attribute["strength"],
                    )
                    for attribute in attributes
                ]
            )
        SubjectiveAttributeRepository.refresh_property_aggregates(photo.property)

    @staticmethod
    def refresh_property_aggregates(property_obj):
        grouped = (
            PhotoSubjectiveAttribute.objects.filter(property=property_obj)
            .values("attribute_token")
            .annotate(strength_mean=Avg("strength"))
        )
        current_tokens = {item["attribute_token"] for item in grouped}

        for item in grouped:
            PropertySubjectiveAttribute.objects.update_or_create(
                property=property_obj,
                attribute_token=item["attribute_token"],
                defaults={"strength_mean": item["strength_mean"]},
            )

        PropertySubjectiveAttribute.objects.filter(property=property_obj).exclude(
            attribute_token__in=current_tokens
        ).delete()
