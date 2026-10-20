"""
Local Disk Storage Engine for CareerMatch AI.
Securely saves uploaded resumes into uploads/ with SHA-256 validation and sanitization.
"""

import os
import uuid
import hashlib
import re
from typing import Dict, Any, Tuple


UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")


def sanitize_filename(filename: str) -> str:
    """Strip dangerous path traversal characters and normalize file name."""
    clean = os.path.basename(filename)
    clean = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", clean)
    return clean or "uploaded_resume.pdf"


class LocalStorageService:
    def __init__(self, upload_dir: str = UPLOADS_DIR):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file_bytes: bytes, original_filename: str) -> Dict[str, Any]:
        """Saves file bytes to disk and returns file metadata."""
        safe_name = sanitize_filename(original_filename)
        file_id = str(uuid.uuid4())
        stored_filename = f"{file_id}_{safe_name}"
        destination_path = os.path.join(self.upload_dir, stored_filename)

        sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        with open(destination_path, "wb") as f:
            f.write(file_bytes)

        return {
            "storage_provider": "LOCAL_STORAGE",
            "file_id": file_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "storage_path": destination_path,
            "file_size_bytes": len(file_bytes),
            "sha256": sha256_hash,
            "download_url": f"/api/resumes/download/{stored_filename}"
        }

    def get_file_bytes(self, storage_path: str) -> bytes:
        if not os.path.exists(storage_path):
            raise FileNotFoundError(f"File not found at {storage_path}")
        with open(storage_path, "rb") as f:
            return f.read()

    def delete_file(self, storage_path: str) -> bool:
        if os.path.exists(storage_path):
            os.remove(storage_path)
            return True
        return False


_local_storage_instance = None

def get_local_storage() -> LocalStorageService:
    global _local_storage_instance
    if _local_storage_instance is None:
        _local_storage_instance = LocalStorageService()
    return _local_storage_instance
