import base64
import json
import re
from typing import Any, Dict

import httpx

from config.env import LMSTUDIO_API_URL, LMSTUDIO_MODEL


def _build_messages_with_image(image_bytes: bytes) -> list[dict[str, Any]]:
    b64 = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:image/png;base64,{b64}"
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Please analyze the image and extract the required information. "
                        "Return a compact JSON object with keys: name (string) and price (number)."
                    ),
                },
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]


async def perform_lmstudio_image_extraction(image_bytes: bytes) -> Dict[str, Any]:
    url = LMSTUDIO_API_URL.rstrip("/") + "/v1/chat/completions"
    payload = {
        "model": LMSTUDIO_MODEL,
        "messages": _build_messages_with_image(image_bytes),
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    content: str = ""
    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        content = json.dumps(data)

    try:
        return json.loads(content)
    except Exception:
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
        return {}