import enum


class ClientErrorMessage(enum.StrEnum):
    NOT_FOUND_TEMPLATE_ERROR = "Шаблон не найден"


class NotificationMethodEnum(enum.StrEnum):
    EMAIL = "email"
