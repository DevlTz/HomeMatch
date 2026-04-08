from django.db.models.signals import post_delete
from django.dispatch import receiver
from apps.properties.models import Properties, PropertiesPhotos
from apps.properties.services import delete_from_cloud

@receiver(post_delete, sender=Properties)
def delete_fatherless_related_models(sender, instance, **kwargs):
    """
    Remove Rooms and RoomsExtras if they are no longer linked to any property.
    """
    # Clean up Rooms
    room = getattr(instance, 'rooms', None)
    if room and not room.properties.exists():
        room.delete()
        
    # Clean up RoomsExtras
    extras = getattr(instance, 'rooms_extras', None)
    if extras and not extras.properties.exists():
        extras.delete()

@receiver(post_delete, sender=PropertiesPhotos)
def delete_photo_from_cloud_on_delete(sender, instance, **kwargs):
    """
    Removes the physical file from Cloudflare R2 when a photo record is deleted.
    """
    if instance.r2_key:
        delete_from_cloud(instance.r2_key)