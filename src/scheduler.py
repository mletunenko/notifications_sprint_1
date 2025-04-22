import asyncio
import datetime
import json
import logging
import sys

import aiohttp
from aio_pika import Message
from apscheduler.schedulers.blocking import BlockingScheduler

from core.config import settings
from core.consts import BIRTHDAY_SUBJECT, BIRTHDAY_TEMPLATE_ID, GENERAL_NOTIFICATIONS_QUEUE
from db.rabbit import RabbitMQConnection

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


async def get_birth_day_profiles(page_number):
    birth_day = datetime.date.today().day
    birth_month = datetime.date.today().month
    page_size = 1
    query_params_str = (
        f"birth_day={birth_day}&birth_month={birth_month}&page_size={page_size}&page_number={page_number}"
    )
    url = (
        f"http://{settings.profile_service.host}:"
        f"{settings.profile_service.port}"
        f"{settings.profile_service.profile_path}/?{query_params_str}"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
            return data


async def create_birthday_task(profile_id):
    body = {
        "template_id": BIRTHDAY_TEMPLATE_ID,
        "profile_id": profile_id,
        "subject": BIRTHDAY_SUBJECT,
        "method": "email",
    }
    json_body = json.dumps(body)
    rabbit = RabbitMQConnection()
    rabbit_channel = await rabbit.get_channel()
    await rabbit_channel.default_exchange.publish(
        Message(body=json_body.encode()),
        routing_key=GENERAL_NOTIFICATIONS_QUEUE,
    )
    logger.info(f"birthday notification task created for profile_id = {profile_id}")
    await rabbit.close()


async def send_birthday_notifications():
    page_number = 1
    while profiles := await get_birth_day_profiles(page_number):
        page_number += 1
        for profile in profiles:
            await create_birthday_task(profile["id"])


def run_async_task():
    asyncio.run(send_birthday_notifications())


scheduler = BlockingScheduler()
scheduler.add_job(run_async_task, "cron", hour=13, minute=8)


if __name__ == "__main__":
    logger.info("Notification scheduler started")
    logger.info(f"{datetime.datetime.now()}")
    scheduler.start()
