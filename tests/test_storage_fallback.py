"""
Unit tests for storage and database local fallback mechanisms.
"""

import os
import pytest
from storage.local_storage import get_local_storage
from database.local_store import get_local_db


@pytest.mark.asyncio
async def test_local_database_fallback_crud():
    db = get_local_db()
    users_col = db.get_collection("test_users")

    # Insert
    doc = {"email": "test@example.com", "name": "Test User"}
    res = await users_col.insert_one(doc)
    doc_id = res.inserted_id
    assert doc_id is not None

    # Find
    found = await users_col.find_one({"_id": doc_id})
    assert found is not None
    assert found["email"] == "test@example.com"

    # Update
    await users_col.update_one({"_id": doc_id}, {"name": "Updated Name"})
    updated = await users_col.find_one({"_id": doc_id})
    assert updated["name"] == "Updated Name"

    # Delete
    deleted = await users_col.delete_one({"_id": doc_id})
    assert deleted is True


def test_local_storage_file_operations():
    storage = get_local_storage()
    dummy_bytes = b"%PDF-1.4 dummy pdf content for testing storage layer"
    meta = storage.save_file(dummy_bytes, "test_resume.pdf")

    assert meta["storage_provider"] == "LOCAL_STORAGE"
    assert os.path.exists(meta["storage_path"])

    # Read
    read_bytes = storage.get_file_bytes(meta["storage_path"])
    assert read_bytes == dummy_bytes

    # Delete
    del_res = storage.delete_file(meta["storage_path"])
    assert del_res is True
    assert not os.path.exists(meta["storage_path"])
