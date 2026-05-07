import logging
from celery import shared_task

logger = logging.getLogger(__name__)

@shared_task
def search_nearby_places(property_id):
    from .models import Properties
    from .services import NearbyPlacesService
    property_obj = Properties.objects.get(id=property_id)
    
    NearbyPlacesService.search(property_obj)
    logger.info(f"Nearby places searched with success for property {property_id}")
