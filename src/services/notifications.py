import json

from aio_pika import Message
from aio_pika.abc import AbstractChannel
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import NotificationModel
from schemas.notifications import CreateTaskSchemaIn, NotificationListParams


class NotificationService:
    @staticmethod
    async def list_notifications(
        session: AsyncSession, query_params: NotificationListParams
    ) -> list[NotificationModel]:
        stmt = select(NotificationModel).order_by(NotificationModel.created_at.desc())
        if query_params.profile_id:
            stmt = stmt.where(NotificationModel.profile_id == query_params.profile_id)
        stmt = stmt.offset(
            (query_params.pagination.page_number - 1) * query_params.pagination.page_size
        ).limit(query_params.pagination.page_size)
        result = await session.execute(stmt)
        notifications_list = list(result.scalars().all())
        return notifications_list

    @staticmethod
    async def create_notification_task(
        data: CreateTaskSchemaIn,
        rabbit_channel: AbstractChannel,
    ) -> None:
        body = {
            "template_id": str(data.template_id),
            "profile_id": str(data.profile_id),
            "subject": data.subject,
            "method": data.method.value,
        }
        json_body = json.dumps(body)
        await rabbit_channel.default_exchange.publish(
            Message(body=json_body.encode()),
            routing_key="notifications",
        )

    @staticmethod
    async def create_welcome_email_task(
        profile_id: UUID4,
        rabbit_channel: AbstractChannel,
    ) -> None:
        body = {
            "template_id": "7606d2de-81a7-4df0-8d38-c0c807ad7615",
            "profile_id": str(profile_id),
            "subject": "Добро пожаловать!",
            "method": "email",
        }
        json_body = json.dumps(body)
        await rabbit_channel.default_exchange.publish(
            Message(body=json_body.encode()),
            routing_key="notifications",
        )
