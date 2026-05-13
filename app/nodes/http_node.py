import httpx


async def execute(config: dict, context: dict) -> dict:
    url = config.get("url", "")
    if not url:
        raise ValueError("HTTPNode needs 'url' in config.")

    method = config.get("method", "GET").upper()
    headers = config.get("headers", {})
    body = config.get("body")
    params = config.get("params", {})

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers,
            json=body if isinstance(body, dict) else None,
            params=params,
        )
        response.raise_for_status()

    try:
        response_body = response.json()
    except Exception:
        response_body = response.text

    return {
        "status_code": response.status_code,
        "body": response_body,
    }