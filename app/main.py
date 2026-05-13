from fastapi import FastAPI
from app.core.models import Pipeline, PipelineCreate

app = FastAPI(
    title = "FlowForge",
    description = "A pipeline execution engine for AI workflows",
    version = "0.1.0",
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "FlowForge"}