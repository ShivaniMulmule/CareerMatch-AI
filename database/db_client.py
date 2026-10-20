"""
Database Provider Selector for CareerMatch AI.
Checks if live MongoDB is reachable; if not, automatically falls back to local JSON store
with clear log messaging. Guarantees the application never crashes due to missing cloud services.
"""

import os
from typing import Any
from database.mongodb import get_mongo_client, DATABASE_NAME
from database.local_store import get_local_db


_db_mode = None
_cached_db = None


async def get_database():
    """
    Returns database handle (MongoDB database object or LocalStore proxy).
    Cached once determined.
    """
    global _db_mode, _cached_db
    if _cached_db is not None:
        return _cached_db

    # Try MongoDB connection
    mongo_client = get_mongo_client()
    if mongo_client is not None:
        try:
            # Ping database with short timeout
            await mongo_client.admin.command("ping")
            _db_mode = "MONGODB"
            _cached_db = mongo_client[DATABASE_NAME]
            print(f"[+] [DATABASE] Connected to live MongoDB ({DATABASE_NAME})")
            return _cached_db
        except Exception as e:
            pass

    # Fallback to local store
    _db_mode = "LOCAL_FALLBACK"
    _cached_db = get_local_db()
    print("[!] [DATABASE] MongoDB unavailable. Operating in secure LOCAL DEVELOPMENT mode (data/local_db.json)")
    return _cached_db


def get_current_db_mode() -> str:
    global _db_mode
    return _db_mode or "LOCAL_FALLBACK"
