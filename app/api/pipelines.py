import time
import uuid
from fastapi import APIRouter, HTTPException
from app.core.models import Pipeline, PipelineCreate
from app.db.mongo import get_db

router = APIRouter()


@router.post("/", response_model=Pipeline, status_code=201)
async def create_pipeline(payload: PipelineCreate):
    db = await get_db()
    pipeline = Pipeline(
        id=str(uuid.uuid4()),
        created_at=time.time(),
        **payload.model_dump(),
    )
    await db.pipelines.insert_one(pipeline.model_dump())
    return pipeline


@router.get("/", response_model=list[Pipeline])
async def list_pipelines():
    db = await get_db()
    docs = await db.pipelines.find({}, {"_id": 0}).to_list(100)
    return docs


@router.get("/{pipeline_id}", response_model=Pipeline)
async def get_pipeline(pipeline_id: str):
    db = await get_db()
    doc = await db.pipelines.find_one({"id": pipeline_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Pipeline nahi mila")
    return doc


@router.delete("/{pipeline_id}", status_code=204)
async def delete_pipeline(pipeline_id: str):
    db = await get_db()
    result = await db.pipelines.delete_one({"id": pipeline_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pipeline nahi mila")