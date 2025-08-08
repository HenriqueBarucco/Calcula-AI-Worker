from helpers.logger import logger

import aio_pika # type: ignore
import json

from services.s3 import download_image_from_minio
from services.llm import perform_lmstudio_image_extraction
from services.calcula_api import send_patch

async def process(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        logger.info(f"Received message: {message.body}")
        try:
            msg = json.loads(message.body)
            photo_id = msg["photo_id"]
            session_id = msg["session_id"]
            image_type = msg["type"]

            image_bytes = download_image_from_minio(photo_id, image_type)

            data = await perform_lmstudio_image_extraction(image_bytes)
            
            name = data.get("name")
            price_str = data.get("price")

            if not name or not price_str:
                raise ValueError("Could not extract valid name/price from image")

            value = float(price_str.replace(",", "."))
            logger.info(f"Extracted: name='{name}', price={value}")

            send_patch(session_id, photo_id, name, value)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)