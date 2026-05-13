from typing import Any


async def execute(config: dict, context: dict) -> Any:
    key = config.get("key", "text")
    inputs = context.get("__inputs__", {})

    if key not in inputs:
        raise ValueError(f"Input key '{key}' missing. Available: {list(inputs.keys())}")

    return inputs[key]