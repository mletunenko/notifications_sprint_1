
from fastapi import APIRouter, Depends, Response
from pydantic import UUID4

from db.postgres import SessionDep
from db.rabbit import RabbitDep
from models import NotificationModel
from schemas.notifications import CreateTaskSchemaIn, NotificationListParams, NotificationSchemaOut
from schemas.services.notifications import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get(path="/", summary="Получить список нотификаций", response_model=list[NotificationSchemaOut])
async def list_notifications(
    session: SessionDep,
    query_params: NotificationListParams = Depends(),
) -> list[NotificationModel]:
    notifications_list = await NotificationService.list_notifications(session, query_params)
    return notifications_list


@router.post(path="/create_task", summary="Поставить в очередь отправку уведомления")
async def create_notification_task(
    data: CreateTaskSchemaIn,
    rabbit_channel: RabbitDep,
):
    await NotificationService.create_notification_task(data, rabbit_channel)
    return Response()


@router.post(
    path="/create_welcome_task",
    summary="Поставить в очередь отправку уведомления зарегестированному пользователю",
)
async def create_welcome_email_task(
    user_id: UUID4,
    rabbit_channel: RabbitDep,
) -> Response:
    await NotificationService.create_welcome_email_task(user_id, rabbit_channel)
    return Response()
