from django.contrib import admin
from apps.ai_analysis.models import PhotoSubjectiveAttribute, PropertySubjectiveAttribute


@admin.register(PhotoSubjectiveAttribute)
class PhotoSubjectiveAttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "photo", "attribute_token", "strength", "updated_at")
    search_fields = ("attribute_token",)
    list_filter = ("attribute_token",)


@admin.register(PropertySubjectiveAttribute)
class PropertySubjectiveAttributeAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "attribute_token", "strength_mean", "updated_at")
    search_fields = ("attribute_token",)
    list_filter = ("attribute_token",)
