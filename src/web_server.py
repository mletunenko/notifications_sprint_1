import asyncio
import logging

import logstash
import sentry_sdk
import uvicorn
from fastapi import APIRouter, FastAPI

from api.notifications.views import router as notifications_router
from api.templates.views import router as templates_router
from core.config import settings
from db.rabbit import RabbitMQConnection

app = FastAPI()

combined_router = APIRouter(prefix="/api")
combined_router.include_router(templates_router)
combined_router.include_router(notifications_router)

app.include_router(combined_router)


logger = logging.getLogger("fastapi-app")
logger.setLevel(logging.INFO)
logger.addHandler(logstash.LogstashHandler(settings.logstash.host, settings.logstash.port, version=1))
logger.info("FastAPI подключен к Logstash!", extra={"tags": ["notifications"]})

if settings.sentry_enable:
    sentry_sdk.init(
        dsn=settings.sentry_sdk,
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

if __name__ == "__main__":
    rabbit = RabbitMQConnection()
    asyncio.run(rabbit.declare_notifications_queue())

    uvicorn.run(
        "web_server:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
