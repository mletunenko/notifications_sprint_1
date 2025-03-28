import json

from aio_pika import Message
from fastapi import APIRouter, Depends, Response
from pydantic import UUID4
from sqlalchemy import select
from starlette.status import HTTP_200_OK

from core.config import settings
from db.postgres import SessionDep
from db.rabbit import RabbitDep
from models import NotificationModel
from schemas.notifications import CreateTaskSchemaIn, NotificationListParams, NotificationSchemaOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get(path="/", summary="Получить список нотификаций")
async def list_notifications(
    session: SessionDep,
    query_params: NotificationListParams = Depends(),
) -> list[NotificationSchemaOut]:
    stmt = select(NotificationModel).order_by(NotificationModel.created_at.desc())
    if query_params.user_id:
        stmt = stmt.where(NotificationModel.user_id == query_params.user_id)
    stmt = stmt.offset((query_params.pagination.page_number - 1) * query_params.pagination.page_size).limit(
        query_params.pagination.page_size
    )
    result = await session.execute(stmt)
    notifications_list = result.scalars().all()
    return notifications_list


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
    return Response()


@router.post(
    path="/create_welcome_task",
    summary="Поставить в очередь отправку уведомления зарегестированному пользователю",
)
async def create_welcome_email_task(
    user_id: UUID4,
    rabbit_chanel: RabbitDep,
) -> Response:
    body = {
        "template_id": settings.welcome_email_template_id,
        "user_id": str(user_id),
        "subject": settings.welcome_email_subject,
        "method": "email",
    }
    json_body = json.dumps(body)
    await rabbit_chanel.declare_queue("notifications", durable=True)
    await rabbit_chanel.default_exchange.publish(
        Message(body=json_body.encode()),
        routing_key="notifications",
    )
    return Response()
