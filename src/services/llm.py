import lmstudio as lms # type: ignore
import json
import asyncio
import re

from config.env import LMSTUDIO_API_URL, LMSTUDIO_MODEL

lms.configure_default_client(LMSTUDIO_API_URL)
model = lms.llm(LMSTUDIO_MODEL)

async def perform_lmstudio_image_extraction(image_bytes: bytes) -> dict:
    image_handle = lms.prepare_image(image_bytes)

    chat = lms.Chat()
    chat.add_user_message("Please analyze the image and extract the required information.", images=[image_handle])

    loop = asyncio.get_running_loop()

    def blocking_call():
        return model.respond(chat)

    response = await loop.run_in_executor(None, blocking_call)
    print(response)

    try:
        response_text = response.content if hasattr(response, 'content') else str(response)
        return json.loads(response_text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", response_text, re.DOTALL)
        if m:
            return json.loads(m.group())
        return {}