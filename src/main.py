import asyncio
import aio_pika # type: ignore

from helpers.logger import logger
from business.process import process

from config.env import (
    RABBITMQ_URL,
    QUEUE_NAME,
    EXCHANGE_NAME,
    PRE_FETCH_COUNT,
)

async def main() -> None:
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel(publisher_confirms=True)

    await channel.set_qos(prefetch_count=PRE_FETCH_COUNT)

    exchange = await channel.declare_exchange(
        EXCHANGE_NAME, aio_pika.ExchangeType.DIRECT, passive=True
    )

    main_queue = await channel.declare_queue(QUEUE_NAME, passive=True)

    async def handler(msg: aio_pika.IncomingMessage) -> None:
        await process(msg, exchange)

    await main_queue.consume(handler)
    logger.info(
        f" [*] Listening on '{QUEUE_NAME}'."
    )
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
