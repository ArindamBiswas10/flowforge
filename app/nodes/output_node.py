from typing import Any


async def execute(config: dict, context: dict) -> Any:
    source_node = config.get("source_node")
    if not source_node:
        raise ValueError("OutputNode needs 'source_node' in config.")

    value = context.get(source_node)
    if value is None:
        raise ValueError(f"OutputNode: '{source_node}' missing in context.")

    field = config.get("field")
    if field and isinstance(value, dict):
        value = value.get(field, value)

    return {
        "label": config.get("label", "output"),
        "value": value,
    }