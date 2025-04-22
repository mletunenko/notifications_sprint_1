import asyncio
import json

import aio_pika

from core.config import settings
from core.consts import (
    GENERAL_NOTIFICATIONS_QUEUE,
    WELCOME_NOTIFICATIONS_QUEUE,
    WELCOME_SUBJECT,
    WELCOME_TEMPLATE_ID,
)
from providers.providers import EmailProvider


async def general_process_message(message: aio_pika.IncomingMessage):
    try:
        message_data = json.loads(message.body.decode())
        if message_data["method"] == "email":
            provider = EmailProvider(
                message_data["template_id"],
                message_data["profile_id"],
                message_data["subject"],
            )
        else:
            raise Exception(f"Unprocessed sending method: {message_data['method']}")

        await provider.prepare_message()
        await provider.send_message()
        await message.ack()

    except Exception as e:
        print(f"Error processing message: {e}")
        await message.nack(requeue=False)


async def welcome_process_message(message: aio_pika.IncomingMessage):
    try:
        message_data = json.loads(message.body.decode())
        provider = EmailProvider(
            WELCOME_TEMPLATE_ID,
            message_data["profile_id"],
            WELCOME_SUBJECT,
        )
        await provider.prepare_message()
        await provider.send_message()
        await message.ack()

    except Exception as e:
        print(f"Error processing message: {e}")
        await message.nack(requeue=False)


async def consume():
    connection = await aio_pika.connect_robust(
        host=settings.rabbit.host,
        login=settings.rabbit.login,
        password=settings.rabbit.password,
    )

    async with connection:
        channel = await connection.channel()
        general_notification_queue = await channel.declare_queue(GENERAL_NOTIFICATIONS_QUEUE, durable=True)
        welcome_notification_queue = await channel.declare_queue(WELCOME_NOTIFICATIONS_QUEUE, durable=True)
        await general_notification_queue.consume(general_process_message, no_ack=False)
        await welcome_notification_queue.consume(welcome_process_message, no_ack=False)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(consume())
