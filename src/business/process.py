from helpers.logger import logger

import aio_pika # type: ignore
import json
from typing import Any

from services.s3 import download_image_from_minio
from services.llm import perform_lmstudio_image_extraction
from services.calcula_api import send_patch, delete_price
from config.env import (
    WAIT_QUEUE_NAME,
    PARKING_LOT_QUEUE_NAME,
    MAX_RETRIES,
    WAIT_ROUTING_KEY,
    PARKING_LOT_ROUTING_KEY,
)


def _get_attempts(msg: dict[str, Any]) -> int:
    try:
        return int(msg.get("attempts", 0))
    except Exception:
        return 0


async def _requeue_wait(exchange: aio_pika.abc.AbstractExchange, msg: dict[str, Any]) -> None:
    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(msg).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=WAIT_ROUTING_KEY,
        mandatory=True,
    )


async def _send_to_parking_lot(exchange: aio_pika.abc.AbstractExchange, msg: dict[str, Any]) -> None:
    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(msg).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=PARKING_LOT_ROUTING_KEY,
        mandatory=True,
    )


async def process(message: aio_pika.IncomingMessage, exchange: aio_pika.abc.AbstractExchange) -> None:
    async with message.process(requeue=False):
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

            value = float(str(price_str).replace(",", "."))
            logger.info(f"Extracted: name='{name}', price={value}")

            send_patch(session_id, photo_id, name, value)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)

            try:
                msg = json.loads(message.body)
            except Exception:
                msg = {"raw": message.body.decode("utf-8", errors="ignore")}

            attempts = _get_attempts(msg) + 1
            msg["attempts"] = attempts

            if attempts < MAX_RETRIES:
                logger.info(
                    f"Requeueing to wait queue '{WAIT_QUEUE_NAME}' with attempts={attempts}/{MAX_RETRIES}"
                )
                await _requeue_wait(exchange, msg)
            else:
                logger.warning(
                    f"Max attempts reached ({attempts}). Sending to parking lot '{PARKING_LOT_QUEUE_NAME}' and performing cleanup."
                )
                await _send_to_parking_lot(exchange, msg)

                try:
                    session_id = str(msg.get("session_id", ""))
                    price_id = str(msg.get("photo_id", ""))
                    if session_id and price_id:
                        delete_price(session_id, price_id)
                    else:
                        logger.warning("Missing session_id or photo_id for DELETE call; skipping.")
                except Exception as del_err:
                    logger.error(f"Error calling DELETE API after parking: {del_err}")