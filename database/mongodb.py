"""
MongoDB Motor Async Client for CareerMatch AI.
Connects to MongoDB in production or configured staging environments.
"""

import os
from typing import Optional, Any

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False


MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "careermatch_ai")

_mongo_client: Optional[Any] = None


def get_mongo_client():
    global _mongo_client
    if not MOTOR_AVAILABLE:
        return None
    if _mongo_client is None:
        try:
            _mongo_client = AsyncIOMotorClient(
                MONGODB_URI,
                serverSelectionTimeoutMS=1500,
                connectTimeoutMS=1500
            )
        except Exception:
            _mongo_client = None
    return _mongo_client


def get_mongo_database():
    client = get_mongo_client()
    if client:
        return client[DATABASE_NAME]
    return None
