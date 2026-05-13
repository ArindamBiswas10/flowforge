# FlowForge

A lightweight pipeline execution engine for AI workflows — built with FastAPI, MongoDB, and Redis.

Inspired by platforms like VectorShift and Langflow. Supports DAG-based node execution, async pipeline runs, and real-time event streaming over SSE.

---

## What it does

- Define pipelines as a graph of nodes and edges
- Execute them asynchronously in the background
- Stream execution events in real-time using Server-Sent Events
- Built-in node types: `input`, `prompt_template`, `llm`, `http`, `output`

---

## Stack

- **FastAPI** — async REST API
- **MongoDB** (via Motor) — pipeline and run storage
- **Redis** — pub/sub event streaming + event replay for late subscribers
- **Groq API** — LLM inference (llama-3.3-70b-versatile)
- **Docker** — local MongoDB and Redis

---

## Project Structure

```
flowforge/
├── app/
│   ├── main.py               # FastAPI app, lifespan hooks
│   ├── api/
│   │   ├── pipelines.py      # CRUD routes for pipelines
│   │   └── runs.py           # Trigger runs, SSE stream
│   ├── core/
│   │   ├── models.py         # Pydantic models (Pipeline, Node, Edge, Run)
│   │   └── executor.py       # DAG resolver + async pipeline executor
│   ├── nodes/
│   │   ├── registry.py       # Maps NodeType → handler function
│   │   ├── input_node.py
│   │   ├── prompt_template_node.py
│   │   ├── llm_node.py       # Groq API call
│   │   ├── http_node.py      # Generic HTTP node
│   │   └── output_node.py
│   └── db/
│       ├── mongo.py          # Motor async client
│       └── redis.py          # Pub/sub + event persistence
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

## How the executor works

Pipelines are defined as a DAG (Directed Acyclic Graph). On execution:

1. **Topological sort** (Kahn's algorithm) resolves execution order
2. Nodes with no dependencies run first — independent nodes run **in parallel** using `asyncio.gather`
3. Each node's output is stored in a shared `context` dict, keyed by node ID
4. Downstream nodes read upstream outputs from context

Cycle detection is built in — if a cycle exists, the run fails immediately with an error.

---

## Real-time streaming

Pipeline runs are async — the trigger endpoint returns a `run_id` immediately (HTTP 202).

Events are published to Redis as each node starts and completes. The `/stream` endpoint opens an SSE connection and delivers these events live.

Events are also persisted in a Redis list, so late subscribers still get the full history — no race condition between triggering a run and opening the stream.

Event types: `connected`, `node_start`, `node_complete`, `run_complete`

---

## Setup

**Requirements:** Python 3.11+, Docker

```bash
git clone https://github.com/YOUR_USERNAME/flowforge
cd flowforge

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=flowforge
REDIS_URL=redis://localhost:6379
GROQ_API_KEY=your_key_here
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

Start MongoDB and Redis:

```bash
docker compose up -d
```

Start the server:

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`

---

## Quick example

**Create a pipeline:**

```bash
curl -X POST http://localhost:8000/pipelines/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simple LLM Pipeline",
    "nodes": [
      { "id": "n_input", "type": "input", "config": { "key": "topic" } },
      { "id": "n_prompt", "type": "prompt_template", "config": { "template": "Explain {n_input} in 2 sentences." } },
      { "id": "n_llm", "type": "llm", "config": { "prompt_node": "n_prompt" } },
      { "id": "n_output", "type": "output", "config": { "source_node": "n_llm", "field": "content" } }
    ],
    "edges": [
      { "source": "n_input", "target": "n_prompt" },
      { "source": "n_prompt", "target": "n_llm" },
      { "source": "n_llm", "target": "n_output" }
    ]
  }'
```

**Trigger a run:**

```bash
curl -X POST http://localhost:8000/runs/{pipeline_id} \
  -H "Content-Type: application/json" \
  -d '{ "inputs": { "topic": "Redis pub/sub" } }'
```

**Stream events:**

```bash
curl -N http://localhost:8000/runs/{run_id}/stream
```

```
data: {"event": "connected", "run_id": "..."}
data: {"event": "node_start", "node_id": "n_input", "node_type": "input"}
data: {"event": "node_complete", "node_id": "n_input", "status": "completed"}
data: {"event": "node_start", "node_id": "n_llm", "node_type": "llm"}
data: {"event": "node_complete", "node_id": "n_llm", "status": "completed"}
data: {"event": "run_complete", "status": "completed"}
```