from typing import Annotated

import aio_pika
from aio_pika.abc import AbstractChannel
from fastapi import Depends

from core.config import settings


class RabbitMQConnection:
    def __init__(self) -> None:
        self.connection = None

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(host=settings.queue_host)
        return self.connection

    async def get_channel(self):
        connection = await self.connect()
        return await connection.channel()


rabbitmq = RabbitMQConnection()


async def get_rabbitmq_channel():
    async with await rabbitmq.get_channel() as channel:
        yield channel


RabbitDep = Annotated[AbstractChannel, Depends(get_rabbitmq_channel)]
