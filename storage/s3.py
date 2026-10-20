"""
AWS S3 Storage Client for CareerMatch AI.
Integrates Amazon S3 for cloud object storage in production environments.
"""

import os
import uuid
import hashlib
from typing import Dict, Any, Optional

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class S3StorageService:
    def __init__(self):
        self.bucket_name = os.getenv("AWS_S3_BUCKET", "")
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.s3_client = None
        
        if BOTO3_AVAILABLE and self.bucket_name and os.getenv("AWS_ACCESS_KEY_ID"):
            try:
                self.s3_client = boto3.client("s3", region_name=self.region)
            except Exception:
                self.s3_client = None

    def is_configured(self) -> bool:
        return self.s3_client is not None and bool(self.bucket_name)

    def save_file(self, file_bytes: bytes, original_filename: str) -> Dict[str, Any]:
        if not self.is_configured():
            raise RuntimeError("AWS S3 is not properly configured.")

        file_id = str(uuid.uuid4())
        key = f"resumes/{file_id}_{original_filename}"
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=file_bytes,
            ContentType="application/pdf"
        )

        presigned_url = self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=3600
        )

        return {
            "storage_provider": "AWS_S3",
            "file_id": file_id,
            "original_filename": original_filename,
            "stored_filename": key,
            "storage_path": f"s3://{self.bucket_name}/{key}",
            "file_size_bytes": len(file_bytes),
            "sha256": sha256_hash,
            "download_url": presigned_url
        }
