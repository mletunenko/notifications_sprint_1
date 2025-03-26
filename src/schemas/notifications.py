from datetime import datetime

from fastapi import Depends
from pydantic import UUID4, BaseModel

from schemas.base import PaginationParams
from utils.enums import NotificationMethodEnum


class CreateTaskSchemaIn(BaseModel):
    template_id: UUID4
    user_id: UUID4
    subject: str | None = None
    method: NotificationMethodEnum


class NotificationSchemaOut(BaseModel):
    created_at: datetime
    user_id: UUID4
    method: str
    address: str
    subject: str | None = None
    content: str


class NotificationListParams(BaseModel):
    # sort: str = Field("-created_at", description="Поле сортировки")
    user_id: UUID4 | None = None
    pagination: PaginationParams = Depends()
