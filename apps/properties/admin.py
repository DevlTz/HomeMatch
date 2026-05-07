from django.contrib import admin
from .models import Condo, Properties, PropertiesPhotos, Reviews, Rooms, RoomsExtras


@admin.register(Properties)
class PropertiesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "city",
        "neighborhood",
        "type",
        "property_purpose",
        "price",
        "owner",
        "created_at",
    )
    list_filter = ("type", "property_purpose", "city")
    search_fields = ("address", "neighborhood", "city")
    # owner, rooms, condo etc. are selected via dropdowns
    # photos are intentionally excluded: upload via POST /api/properties/{id}/photos/ instead
    exclude = ("embedding",)  # hides the raw embedding field from the form


@admin.register(PropertiesPhotos)
class PropertiesPhotosAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "order")
    readonly_fields = ("r2_key",)  # show it but don't let anyone edit it manually


@admin.register(Rooms)
class RoomsAdmin(admin.ModelAdmin):
    list_display = ("id", "bedrooms", "bathrooms", "parking_spots")


@admin.register(RoomsExtras)
class RoomsExtrasAdmin(admin.ModelAdmin):
    list_display = ("id", "living_room", "garden", "kitchen", "pool", "office")


@admin.register(Condo)
class CondoAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "gym", "pool", "court")


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "user", "rating", "created_at")
