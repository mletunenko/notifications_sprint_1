import json

from aio_pika import Message
from fastapi import APIRouter, Response
from starlette.status import HTTP_200_OK

from db.rabbit import RabbitDep
from schemas.notifications import CreateTaskSchemaIn

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post(path="/create_task", summary="Поставить в очередь отправку уведомления")
async def create_notification_task(
    data: CreateTaskSchemaIn,
    rabbit_chanel: RabbitDep,
):
    body = {
        "template_id": str(data.template_id),
        "user_id": str(data.user_id),
        "subject": data.subject,
        "method": data.method.value,
    }
    json_body = json.dumps(body)
    await rabbit_chanel.declare_queue("notifications", durable=True)
    await rabbit_chanel.default_exchange.publish(
        Message(body=json_body.encode()),
        routing_key="notifications",
    )
    return Response(status_code=HTTP_200_OK)
