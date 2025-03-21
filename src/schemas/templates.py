from datetime import datetime

from pydantic import UUID4, BaseModel


class TemplateSchemaIn(BaseModel):
    body: str


class TemplateSchemaOut(BaseModel):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    body: str


class TemplateListParams(BaseModel):
    body: str | None = None
