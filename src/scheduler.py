import asyncio
import datetime
import json
import logging
import sys

import aiohttp
from aio_pika import Message
from apscheduler.schedulers.blocking import BlockingScheduler

from core.config import settings
from db.rabbit import RabbitMQConnection

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


async def get_birth_day_users(page_number):
    birth_day = datetime.date.today().day
    birth_month = datetime.date.today().month
    page_size = 1
    query_params_str = (
        f"birth_day={birth_day}&birth_month={birth_month}&page_size={page_size}&page_number={page_number}"
    )
    url = f"http://{settings.auth_host}:{settings.auth_port}{settings.user_path}/?{query_params_str}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data


async def create_birthday_task(user_id):
    body = {
        "template_id": "9548333e-93aa-4ee7-8987-cc66e0a486ae",
        "user_id": user_id,
        "subject": "С Днём Рождения!",
        "method": "email",
    }
    json_body = json.dumps(body)
    rabbit = RabbitMQConnection()
    rabbit_channel = await rabbit.get_channel()
    await rabbit_channel.declare_queue("notifications", durable=True)
    await rabbit_channel.default_exchange.publish(
        Message(body=json_body.encode()),
        routing_key="notifications",
    )
    logger.info(f"birthday notification task created for user_id = {user_id}")
    await rabbit.close()


async def send_birthday_notifications(user_id=None):
    page_number = 1
    while users := await get_birth_day_users(page_number):
        page_number += 1
        for user in users:
            await create_birthday_task(user["id"])


def run_async_task():
    asyncio.run(send_birthday_notifications())


scheduler = BlockingScheduler()
scheduler.add_job(run_async_task, "cron", hour=9, minute=38)


if __name__ == "__main__":
    logger.info("Notification scheduler started")
    logger.info(f"{datetime.datetime.now()}")
    scheduler.start()
