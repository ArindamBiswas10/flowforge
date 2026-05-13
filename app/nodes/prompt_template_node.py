import re
from typing import Any


async def execute(config: dict, context: dict) -> str:
    template = config.get("template", "")
    if not template:
        raise ValueError("PromptTemplateNode needs 'template' in config.")

    def resolve(match):
        key = match.group(1)
        val = context.get(key)
        if val is None:
            return f"{{{key}}}"
        return str(val)

    return re.sub(r"\{(\w+)\}", resolve, template)