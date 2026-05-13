from enum import Enum
from typing import Any,Optional
from pydantic import BaseModel, Field
import uuid

class NodeType(str,Enum):
    INPUT = "input"
    PROMPT_TEMPLATE = "prompt_template"
    LLM = "llm"
    HTTP = "http"
    OUTPUT = "output"


class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    type: NodeType
    label: str = ""
    config: dict[str,Any] = {}

class Edge(BaseModel):
    source: str
    target: str

class Pipeline(BaseModel):
    id:str = Field(default_factory=lambda: str(uuid.uuid4()))
    name:str
    description: str = ""
    nodes: list[Node]
    edges: list[Edge]


class PipelineCreate(BaseModel):
    name:str
    description: str = ""
    nodes: list[Node]
    edges: list[Edge]

class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class PipelineRun(BaseModel):
    id: str
    pipeline_id: str
    status: RunStatus = RunStatus.QUEUED
    error: str = None


class RunCreate(BaseModel):
    inputs: dict[str, Any] = {}
