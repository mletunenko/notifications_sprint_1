from fastapi import APIRouter, Depends, Response
from pydantic import UUID4
from starlette.status import HTTP_204_NO_CONTENT

from db.postgres import SessionDep
from models import TemplateModel
from schemas.templates import TemplateListParams, TemplateSchemaIn, TemplateSchemaOut
from services.templates import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", summary="Получить список шаблонов", response_model=list[TemplateSchemaOut])
async def get_templates_list(
    session: SessionDep, query_params: TemplateListParams = Depends()
) -> list[TemplateModel]:
    template_list = await TemplateService.get_templates_list(session, query_params)
    return template_list


@router.get("/{template_id}", summary="Получить шаблон по id", response_model=TemplateSchemaOut)
async def get_template(template_id: UUID4, session: SessionDep) -> TemplateModel:
    template = await TemplateService.get_template(template_id, session)
    return template


@router.post("", summary="Создать шаблон", response_model=TemplateSchemaOut)
async def create_template(data: TemplateSchemaIn, session: SessionDep) -> TemplateModel:
    new_template = await TemplateService.create_template(data, session)
    return new_template


@router.patch(path="/{template_id}", summary="Обновление шаблона", response_model=TemplateSchemaOut)
async def update_template(
    template_id: UUID4,
    data: TemplateSchemaIn,
    session: SessionDep,
) -> TemplateModel:
    template = await TemplateService.update_template(template_id, data, session)
    return template


@router.delete(path="/{template_id}", summary="Удалить шаблон")
async def delete_template(template_id: UUID4, session: SessionDep) -> Response:
    await TemplateService.delete_template(template_id, session)
    return Response(status_code=HTTP_204_NO_CONTENT)
