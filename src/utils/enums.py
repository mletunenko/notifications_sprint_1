import enum
from enum import Enum


class ClientErrorMessage(Enum):
    NOT_FOUND_TEMPLATE_ERROR = "Шаблон не найден"


class NotificationMethodEnum(enum.Enum):
    EMAIL = "email"
