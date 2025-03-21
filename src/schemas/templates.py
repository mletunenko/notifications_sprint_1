from datetime import datetime

from pydantic import UUID4, BaseModel


class TemplateSchemaIn(BaseModel):
    code: str


class TemplateSchemaOut(BaseModel):
    id: UUID4
    created_at: datetime
    updated_at: datetime
    code: str


class TemplateListParams(BaseModel):
    code: str | None = None
