import enum

from pydantic import UUID4, BaseModel


class NotificationMethodEnum(enum.Enum):
    EMAIL = "email"
    SMS = "sms"


class CreateTaskSchemaIn(BaseModel):
    template_id: UUID4
    user_id: UUID4
    subject: str | None = None
    method: NotificationMethodEnum
