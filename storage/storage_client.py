"""
Storage Provider Selector for CareerMatch AI.
Resolves to AWS S3 if credentials are configured; otherwise automatically falls back
to secure local disk storage (uploads/) with clear diagnostic logging.
"""

from typing import Dict, Any
from storage.local_storage import get_local_storage
from storage.s3 import S3StorageService


_s3_service = None
_storage_mode = None


def get_storage():
    global _s3_service, _storage_mode
    if _s3_service is None:
        _s3_service = S3StorageService()
        if _s3_service.is_configured():
            _storage_mode = "AWS_S3"
            print(f"[+] [STORAGE] AWS S3 connected (Bucket: {_s3_service.bucket_name})")
        else:
            _storage_mode = "LOCAL_STORAGE"
            print("[!] [STORAGE] AWS S3 credentials not configured. Operating in secure LOCAL STORAGE mode (uploads/)")

    if _storage_mode == "AWS_S3":
        return _s3_service
    return get_local_storage()


def get_current_storage_mode() -> str:
    global _storage_mode
    if _storage_mode is None:
        get_storage()
    return _storage_mode
