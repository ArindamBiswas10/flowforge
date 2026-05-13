import os
import httpx


async def execute(config: dict, context: dict) -> dict:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY nahi mila .env mein.")

    prompt_node_id = config.get("prompt_node")
    if prompt_node_id:
        user_message = str(context.get(prompt_node_id, ""))
    else:
        user_message = config.get("prompt", "")

    if not user_message:
        raise ValueError("LLMNode ko 'prompt_node' ya 'prompt' chahiye config mein.")

    payload = {
        "model": config.get("model", "llama-3.3-70b-versatile"),
        "temperature": config.get("temperature", 0.7),
        "max_tokens": config.get("max_tokens", 512),
        "messages": [
            {"role": "system", "content": config.get("system", "You are a helpful assistant.")},
            {"role": "user", "content": user_message},
        ],
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
        )
        if response.status_code != 200:
            print("Groq error:", response.text)
            response.raise_for_status()
        data = response.json()

    return {
        "content": data["choices"][0]["message"]["content"],
        "model": data.get("model"),
        "usage": data.get("usage", {}),
    }