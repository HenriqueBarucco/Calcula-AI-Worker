import base64
import json
import re
from typing import Any, Dict
import asyncio

import httpx

from helpers.logger import logger
from config.env import (
    LMSTUDIO_API_URL,
    LMSTUDIO_MODEL,
    LMSTUDIO_TIMEOUT_SECONDS,
    LMSTUDIO_MAX_RETRIES,
    LMSTUDIO_RETRY_BASE_DELAY,
)


def _guess_mime(image_bytes: bytes) -> str:
    if len(image_bytes) >= 4:
        if image_bytes[:2] == b"\xff\xd8":
            return "image/jpeg"
        if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
            return "image/png"
        if image_bytes[:6] in (b"GIF87a", b"GIF89a"):
            return "image/gif"
        if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
            return "image/webp"
    return "application/octet-stream"


def _build_messages_with_image(image_bytes: bytes) -> list[dict[str, Any]]:
    b64 = base64.b64encode(image_bytes).decode("ascii")
    mime = _guess_mime(image_bytes)
    data_url = f"data:{mime};base64,{b64}"
    logger.info(f"LMStudio payload image size (base64 chars)={len(b64):,}")
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
        "temperature": 0,
        "max_tokens": 200,
    }

    headers = {"Content-Type": "application/json"}

    timeout = httpx.Timeout(
        connect=min(10.0, float(LMSTUDIO_TIMEOUT_SECONDS)),
        read=float(LMSTUDIO_TIMEOUT_SECONDS),
        write=min(30.0, float(LMSTUDIO_TIMEOUT_SECONDS)),
        pool=None,
    )

    last_err: Exception | None = None
    attempt = 0
    limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        while attempt <= LMSTUDIO_MAX_RETRIES:
            try:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                break
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.WriteError, httpx.RemoteProtocolError) as e:
                last_err = e
                if attempt >= LMSTUDIO_MAX_RETRIES:
                    raise
                delay = LMSTUDIO_RETRY_BASE_DELAY * (2 ** attempt)
                delay = min(delay, 10.0)
                await asyncio.sleep(delay)
                attempt += 1
            except httpx.HTTPError as e:
                status = getattr(e.response, "status_code", None)
                if status == 408 and attempt < LMSTUDIO_MAX_RETRIES:
                    await asyncio.sleep(1.0 * (2 ** attempt))
                    attempt += 1
                    continue
                raise

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