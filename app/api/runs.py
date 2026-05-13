import uuid
import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse

from app.core.models import Pipeline, PipelineRun, RunCreate, RunStatus
from app.core.executor import execute_pipeline
from app.db.mongo import get_db
from app.db.redis import subscribe_run

router = APIRouter()


@router.post("/{pipeline_id}", status_code=202)
async def trigger_run(pipeline_id: str, payload: RunCreate, background_tasks: BackgroundTasks):
    db = await get_db()
    doc = await db.pipelines.find_one({"id": pipeline_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Pipeline nahi mila")

    pipeline = Pipeline(**doc)
    run_id = str(uuid.uuid4())

    background_tasks.add_task(execute_pipeline, pipeline, run_id, payload.inputs)
    return {"run_id": run_id, "status": "queued"}


@router.get("/{run_id}/stream")
async def stream_run(run_id: str):
    async def event_generator():
        from app.db.redis import get_redis
        r = await get_redis()
        
        yield f"data: {json.dumps({'event': 'connected', 'run_id': run_id})}\n\n"
        
        # Replay stored events for late subscribers
        stored = await r.lrange(f"run:events:{run_id}", 0, -1)
        for item in stored:
            yield f"data: {item}\n\n"
        
        # Check karo kya already complete hai
        if stored and json.loads(stored[-1]).get("event") == "run_complete":
            return
        
        # Warna live subscribe karo
        pubsub = await subscribe_run(run_id)
        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                data = json.loads(message["data"])
                yield f"data: {json.dumps(data)}\n\n"
                if data.get("event") == "run_complete":
                    break
        finally:
            await pubsub.unsubscribe(f"run:{run_id}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )

