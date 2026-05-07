import uuid
from pathlib import Path

import boto3
from botocore.config import Config
from django.conf import settings


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
