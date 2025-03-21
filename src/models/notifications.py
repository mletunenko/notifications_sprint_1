import enum

from pydantic import UUID4
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Enum, ForeignKey

from models import Base


class NotificationMethodEnum(enum.Enum):
    EMAIL = "email"
    SMS = "sms"


class NotificationModel(Base):
    __tablename__ = "notifications"
    method: Mapped[NotificationMethodEnum] = mapped_column(Enum(NotificationMethodEnum, name="notification_method"))
    user_id: Mapped[UUID4] = mapped_column()
    address: Mapped[str] = mapped_column()
    subject: Mapped[str] = mapped_column(nullable=True)
    content: Mapped[str] = mapped_column()