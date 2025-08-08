import asyncio
import aio_pika # type: ignore

from helpers.logger import logger
from business.process import process

from config.env import RABBITMQ_URL, QUEUE_NAME

async def main() -> None:
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.consume(process)
    logger.info(f" [*] Listening on '{QUEUE_NAME}'. Press CTRL+C to exit.")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
