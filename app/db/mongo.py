import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client = None
_db = None


async def connect_mongo():
    global _client, _db
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB", "flowforge")
    _client = AsyncIOMotorClient(uri)
    _db = _client[db_name]
    await _db.pipelines.create_index("id", unique=True)
    await _db.runs.create_index("id", unique=True)


async def close_mongo():
    if _client:
        _client.close()


async def get_db() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("MongoDB connected nahi hai.")
    return _db