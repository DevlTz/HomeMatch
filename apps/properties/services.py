import uuid
import requests
import math
from pathlib import Path

import boto3
from botocore.config import Config
from django.conf import settings
from .models import NearbyPlaces

class NomatimService:
    BASE_URL = "https://nominatim.openstreetmap.org/search"

    @staticmethod
    def geocode(property_obj):
        params = {
            "q": f"{property_obj.address}, {property_obj.city}",
            "format": "json",
            "limit": 1
        }
        headers = {
            "User-Agent": "HomeMatch/1.0"
        }
        response = requests.get(NominatimService.BASE_URL, params=params, headers=headers)
        data = response.json()

        if data:
            property_obj.latitude = float(data[0]["lat"])
            property_obj.longitude = float(data[0]["lon"])
            property_obj.save(update_fields=["latitude", "longitude"])


class CloudService:
    s3_client = boto3.client(

def _use_local():
    return getattr(settings, "USE_LOCAL_STORAGE", False)


# Local storage backend


def _local_upload(image):
    """Save uploaded file to MEDIA_ROOT/properties/ and return a relative key."""
    upload_dir = Path(settings.MEDIA_ROOT) / "properties"
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(image.name).suffix or ".jpg"
    r2_key = f"properties/{uuid.uuid4()}{ext}"
    dest = Path(settings.MEDIA_ROOT) / r2_key

    with open(dest, "wb") as f:
        for chunk in image.chunks():
            f.write(chunk)

    return r2_key


def _local_delete(r2_key):
    path = Path(settings.MEDIA_ROOT) / r2_key
    if path.exists():
        path.unlink()


def _local_url(r2_key):
    """Return a URL served by Django's MEDIA_URL (works in dev with runserver)."""
    return f"{settings.MEDIA_URL}{r2_key}"


# R2 backend


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4")
    )

    @staticmethod
    def upload_to_cloud(image):
        r2_key = f"properties/{uuid.uuid4()}/{image.name}"
        
        CloudService.s3_client.upload_fileobj(
            image,
            settings.R2_BUCKET_NAME,
            r2_key,
            ExtraArgs={"ContentType": image.content_type}
        )
        
        return r2_key

    @staticmethod
    def delete_from_cloud(r2_key):
        CloudService.s3_client.delete_object(
            Bucket=settings.R2_BUCKET_NAME,
            Key=r2_key
        )
    @staticmethod
    def generate_url(r2_key):
        return CloudService.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.R2_BUCKET_NAME, "Key": r2_key},
            ExpiresIn=3600




                )

class NearbyPlacesService:
    CATEGORIES = [("R", "Restaurant"), ("G", "Gym"), ("S", "School"), ("H", "Hospital"), ("SM", "Supermarket"), ("P", "Park")]
    RADIUS = 3000

    @staticmethod
    def search_categories(lat, long, type):
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": "places.displayName,places.rating,places.location"
        }
        body = {
            "includedTypes": [type],
            "maxResultCount": 5,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": long},
                    "radius": NearbyPlacesService.RADIUS
                }
            }
        }
        response = requests.post(url, json=body, headers=headers)
        data = response.json()
        return data.get("places", [])
    
    @staticmethod
    def calculate_distance(lat1, long1, lat2, long2):
        R = 637100
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(long2 - long1)

        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)

    @staticmethod
    def search(property):
        lat = property.latitude
        long = property.longitude

        for category_code, category_type in NearbyPlacesService.CATEGORIES:
            places = NearbyPlacesService.search_categories(lat, long, category_type)
            for place in places:
                place_lat = place["location"]["latitude"]
                place_long = place["location"]["longitude"]
                NearbyPlaces.objects.update_or_create(
                    property=property,
                    name=place["displayName"]["text"],
                    category=category_code,
                    defaults={
                        "distance_meters": NearbyPlacesService.calculate_distance(lat, long, place_lat, place_long),
                        "rating": place.get("rating")
                    }
                )

        config=Config(signature_version="s3v4"),
    )


def _r2_upload(image):
    r2_key = f"properties/{uuid.uuid4()}/{image.name}"
    _get_s3_client().upload_fileobj(
        image,
        settings.R2_BUCKET_NAME,
        r2_key,
        ExtraArgs={"ContentType": image.content_type},
    )
    return r2_key


def _r2_delete(r2_key):
    _get_s3_client().delete_object(Bucket=settings.R2_BUCKET_NAME, Key=r2_key)


def _r2_url(r2_key):
    return _get_s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.R2_BUCKET_NAME, "Key": r2_key},
        ExpiresIn=3600,
    )


# Public interface (used by the rest of the codebase)


def upload_to_cloud(image):
    return _local_upload(image) if _use_local() else _r2_upload(image)


def delete_from_cloud(r2_key):
    if _use_local():
        _local_delete(r2_key)
    else:
        _r2_delete(r2_key)


def generate_url(r2_key):
    return _local_url(r2_key) if _use_local() else _r2_url(r2_key)
