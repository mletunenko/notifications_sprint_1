import asyncio
import json
import aio_pika

from core.config import settings
from providers import EmailProvider


async def process_message(message: aio_pika.IncomingMessage):
    try:
        message_data = json.loads(message.body.decode())
        if message_data["method"] == "email":
            provider = EmailProvider(
                message_data["template_id"],
                message_data["user_id"],
                message_data["subject"],
            )
        else:
            raise Exception(f"Unprocessed sending method: {message_data['method']}")

        await provider.prepare_message()
        await provider.send_message()
        await message.ack()

    except Exception as e:
        print(f"Error processing message: {e}")
        await message.nack(requeue=True)


async def consume():
    connection = await aio_pika.connect_robust(host=settings.queue_host)

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("notifications", durable=True)
        await queue.consume(process_message, no_ack=False)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(consume())
