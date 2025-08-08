import boto3 # type: ignore

from helpers.logger import logger
from botocore.client import Config # type: ignore

from config.env import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)

def download_image_from_minio(photo_id: str, image_type: str) -> bytes:
    key = f"{photo_id}.{image_type}"
    logger.info(f"Downloading image from MinIO: {key}")
    obj = s3_client.get_object(Bucket=MINIO_BUCKET, Key=key)
    return obj["Body"].read()