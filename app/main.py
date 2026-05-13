from fastapi import FastAPI
from app.core.models import Pipeline, PipelineCreate
from contextlib import asynccontextmanager
from app.db.mongo import connect_mongo, close_mongo
from app.db.redis import connect_redis, close_redis
from app.api.pipelines import router as pipeline_router
from app.api.runs import router as run_router
from dotenv import load_dotenv
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_mongo()
    await connect_redis()
    yield
    await close_mongo()
    await close_redis()

app = FastAPI(
    title = "FlowForge",
    description = "A pipeline execution engine for AI workflows",
    version = "0.1.0",
    lifespan = lifespan,
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FlowForge"}

app.include_router(pipeline_router, prefix="/pipelines", tags=["pipelines"])
app.include_router(run_router, prefix="/runs", tags=["runs"])