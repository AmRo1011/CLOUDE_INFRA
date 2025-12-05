"""
S3 client for document storage
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class S3Client:
    """S3 client wrapper"""
    
    def __init__(self):
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize S3 client"""
        config = {
            "region_name": settings.AWS_REGION
        }
        
        if settings.S3_ENDPOINT_URL:
            config["endpoint_url"] = settings.S3_ENDPOINT_URL
        
        if settings.AWS_ACCESS_KEY_ID:
            config["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            config["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
        
        self._client = boto3.client("s3", **config)
    
    async def upload_file(self, file_obj: BinaryIO, key: str, content_type: str) -> bool:
        """Upload file to S3"""
        try:
            self._client.upload_fileobj(
                file_obj,
                settings.S3_BUCKET,
                key,
                ExtraArgs={"ContentType": content_type}
            )
            logger.info(f"Uploaded file to s3://{settings.S3_BUCKET}/{key}")
            return True
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return False
    
    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate presigned URL for download"""
        try:
            url = self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": settings.S3_BUCKET, "Key": key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from S3"""
        try:
            self._client.delete_object(Bucket=settings.S3_BUCKET, Key=key)
            logger.info(f"Deleted file s3://{settings.S3_BUCKET}/{key}")
            return True
        except ClientError as e:
            logger.error(f"S3 delete failed: {e}")
            return False
    
    async def download_file(self, key: str) -> Optional[bytes]:
        """Download file from S3"""
        try:
            response = self._client.get_object(Bucket=settings.S3_BUCKET, Key=key)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            return None


s3_client = S3Client()

