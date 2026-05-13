from collections import defaultdict, deque
from app.core.models import Pipeline
import asyncio
import time
from typing import Any
from app.nodes.registry import get_node_handler

def resolve_execution_order(pipeline: Pipeline) -> list[list[str]]:
    in_degree = {node.id: 0 for node in pipeline.nodes}
    dependents = defaultdict(list)

    for edge in pipeline.edges:
        in_degree[edge.target] += 1
        dependents[edge.source].append(edge.target)

    queue = deque(nid for nid, deg in in_degree.items() if deg == 0)
    groups = []
    visited = 0

    while queue:
        group = list(queue)
        queue.clear()
        groups.append(group)
        for nid in group:
            visited += 1
            for dep in dependents[nid]:
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

    if visited != len(pipeline.nodes):
        raise ValueError("Pipeline has a cycle - DAG is not resolved")
    
    return groups


async def execute_pipeline(pipeline: Pipeline, run_id: str, inputs: dict[str, Any]) -> dict:
    context = {"__inputs__": inputs}
    results = {}

    try:
        groups = resolve_execution_order(pipeline)
    except ValueError as e:
        return {"status": "failed", "error": str(e)}
    
    nodes_map = {node.id: node for node in pipeline.nodes}

    for group in groups:
        tasks = [
            _execute_node(node_map[nid], context)
            for nid in group
        ]
        await asyncio.gather(*tasks)

    return {"status": "completed", "context": context}

async def _execute_node(node, context: dict):
    handler = get_node_handler(node.type)
    output = await handler(node.config, context)
    context[node.id] = output