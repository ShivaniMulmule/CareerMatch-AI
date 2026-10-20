"""
Local JSON Database Engine for CareerMatch AI.
Provides atomic, file-backed CRUD operations replicating Motor/PyMongo collections
for 100% offline local development without external MongoDB dependency.
"""

import os
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional


LOCAL_DB_FILE = os.path.join("data", "local_db.json")


class LocalCollection:
    def __init__(self, name: str, db_manager: "LocalStore"):
        self.name = name
        self.db_manager = db_manager

    async def insert_one(self, document: Dict[str, Any]) -> Any:
        doc = dict(document)
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        if "created_at" not in doc:
            doc["created_at"] = datetime.now().isoformat()
        if "updated_at" not in doc:
            doc["updated_at"] = datetime.now().isoformat()

        async with self.db_manager.lock:
            data = self.db_manager._read_data()
            if self.name not in data:
                data[self.name] = []
            data[self.name].append(doc)
            self.db_manager._write_data(data)

        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertResult(doc["_id"])

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        async with self.db_manager.lock:
            data = self.db_manager._read_data()
            items = data.get(self.name, [])
            for item in items:
                if self._matches(item, query):
                    return dict(item)
            return None

    async def find(self, query: Dict[str, Any], sort: Optional[List[tuple]] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        async with self.db_manager.lock:
            data = self.db_manager._read_data()
            items = data.get(self.name, [])
            matched = [dict(item) for item in items if self._matches(item, query)]

            if sort:
                for field, order in reversed(sort):
                    reverse = (order == -1 or order == "desc")
                    matched.sort(key=lambda x: x.get(field, ""), reverse=reverse)

            if limit:
                matched = matched[:limit]

            return matched

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        async with self.db_manager.lock:
            data = self.db_manager._read_data()
            items = data.get(self.name, [])
            for i, item in enumerate(items):
                if self._matches(item, query):
                    if "$set" in update:
                        item.update(update["$set"])
                    else:
                        item.update(update)
                    item["updated_at"] = datetime.now().isoformat()
                    data[self.name][i] = item
                    self.db_manager._write_data(data)
                    return True
            return False

    async def delete_one(self, query: Dict[str, Any]) -> bool:
        async with self.db_manager.lock:
            data = self.db_manager._read_data()
            items = data.get(self.name, [])
            for i, item in enumerate(items):
                if self._matches(item, query):
                    items.pop(i)
                    data[self.name] = items
                    self.db_manager._write_data(data)
                    return True
            return False

    async def count_documents(self, query: Dict[str, Any]) -> int:
        docs = await self.find(query)
        return len(docs)

    def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        for k, v in query.items():
            if k == "_id" and str(doc.get("_id")) == str(v):
                continue
            if doc.get(k) != v:
                return False
        return True


class LocalStore:
    _instance = None

    def __new__(cls, filepath: str = LOCAL_DB_FILE):
        if cls._instance is None:
            cls._instance = super(LocalStore, cls).__new__(cls)
            cls._instance.filepath = filepath
            cls._instance.lock = asyncio.Lock()
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            if not os.path.exists(filepath):
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump({"users": [], "resumes": [], "jobs": [], "analyses": [], "recommendations": []}, f, indent=2)
        return cls._instance

    def _read_data(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": [], "resumes": [], "jobs": [], "analyses": [], "recommendations": []}

    def _write_data(self, data: Dict[str, Any]) -> None:
        temp_file = f"{self.filepath}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if os.path.exists(self.filepath):
            os.replace(temp_file, self.filepath)
        else:
            os.rename(temp_file, self.filepath)

    def get_collection(self, name: str) -> LocalCollection:
        return LocalCollection(name, self)


def get_local_db() -> LocalStore:
    return LocalStore()
