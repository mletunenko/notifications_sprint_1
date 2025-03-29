import json

from aio_pika import Message
from fastapi import APIRouter, Depends, Response
from pydantic import UUID4
from sqlalchemy import select

from db.postgres import SessionDep
from db.rabbit import RabbitDep
from models import NotificationModel
from schemas.notifications import CreateTaskSchemaIn, NotificationListParams, NotificationSchemaOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get(path="/", summary="Получить список нотификаций", response_model=list[NotificationSchemaOut])
async def list_notifications(
    session: SessionDep,
    query_params: NotificationListParams = Depends(),
) -> list[NotificationModel]:
    stmt = select(NotificationModel).order_by(NotificationModel.created_at.desc())
    if query_params.user_id:
        stmt = stmt.where(NotificationModel.user_id == query_params.user_id)
    stmt = stmt.offset((query_params.pagination.page_number - 1) * query_params.pagination.page_size).limit(
        query_params.pagination.page_size
    )
    result = await session.execute(stmt)
    notifications_list = list(result.scalars().all())
    return notifications_list


@router.post(path="/create_task", summary="Поставить в очередь отправку уведомления")
async def create_notification_task(
    data: CreateTaskSchemaIn,
    rabbit_channel: RabbitDep,
):
    body = {
        "template_id": str(data.template_id),
        "user_id": str(data.user_id),
        "subject": data.subject,
        "method": data.method.value,
    }
    json_body = json.dumps(body)
    await rabbit_channel.default_exchange.publish(
        Message(body=json_body.encode()),
        routing_key="notifications",
    )
    return Response()


@router.post(
    path="/create_welcome_task",
    summary="Поставить в очередь отправку уведомления зарегестированному пользователю",
)
async def create_welcome_email_task(
    user_id: UUID4,
    rabbit_channel: RabbitDep,
) -> Response:
    body = {
        "template_id": "7606d2de-81a7-4df0-8d38-c0c807ad7615",
        "user_id": str(user_id),
        "subject": "Добро пожаловать!",
        "method": "email",
    }
    json_body = json.dumps(body)
    await rabbit_channel.default_exchange.publish(
        Message(body=json_body.encode()),
        routing_key="notifications",
    )
    return Response()
