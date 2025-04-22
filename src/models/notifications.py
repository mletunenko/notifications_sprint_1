from pydantic import UUID4
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from utils.enums import NotificationMethodEnum

from .base import Base


class NotificationModel(Base):
    __tablename__ = "notifications"
    profile_id: Mapped[UUID4] = mapped_column()
    method: Mapped[NotificationMethodEnum] = mapped_column(
        Enum(NotificationMethodEnum, name="notification_method")
    )
    address: Mapped[str] = mapped_column()
    subject: Mapped[str] = mapped_column(nullable=True)
    content: Mapped[str] = mapped_column()
