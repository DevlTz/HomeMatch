import boto3
import uuid
from botocore.config import Config
from django.conf import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.R2_ACCESS_KEY_ID,
    aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4")
)

def upload_to_cloud(image):
    r2_key = f"properties/{uuid.uuid4()}/{image.name}"
    
    s3_client.upload_fileobj(
        image,
        settings.R2_BUCKET_NAME,
        r2_key,
        ExtraArgs={"ContentType": image.content_type}
    )
    
    return r2_key

def delete_from_cloud(r2_key):
    s3_client.delete_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=r2_key
    )

def generate_url(r2_key):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.R2_BUCKET_NAME, "Key": r2_key},
        ExpiresIn=3600
                )
