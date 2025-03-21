from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import UUID4
from sqlalchemy import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from api.enums import ClientErrorMessage
from db.postgres import SessionDep
from models import TemplateModel
from schemas.templates import TemplateListParams, TemplateSchemaIn, TemplateSchemaOut

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", summary="Получить список шаблонов")
async def get_templates_list(
    session: SessionDep, query_params: TemplateListParams = Depends()
) -> list[TemplateSchemaOut]:
    stmt = select(TemplateModel)
    if query_params.body:
        like = f"%{query_params.body}%"
        stmt = stmt.filter(TemplateModel.body.ilike(like))
    result = await session.execute(stmt)
    obj_list = result.scalars().all()
    response = [TemplateSchemaOut.model_validate(obj, from_attributes=True) for obj in obj_list]
    return response


@router.get("/{template_id}", summary="Получить шаблон по id")
async def get_template(template_id: UUID4, session: SessionDep) -> TemplateSchemaOut:
    stmt = select(TemplateModel).where(TemplateModel.id == template_id)
    result = await session.execute(stmt)
    obj = result.scalars().first()
    if not obj:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=ClientErrorMessage.NOT_FOUND_TEMPLATE_ERROR.value
        )
    response = TemplateSchemaOut.model_validate(obj, from_attributes=True)
    return response


@router.post("", summary="Создать шаблон")
async def create_template(data: TemplateSchemaIn, session: SessionDep) -> TemplateSchemaOut:
    new_obj = TemplateModel(body=data.body)
    session.add(new_obj)
    await session.commit()
    response = TemplateSchemaOut.model_validate(new_obj, from_attributes=True)
    return response


@router.patch(path="/{template_id}", summary="Обновление шаблона")
async def update_template(
    template_id: UUID4,
    data: TemplateSchemaIn,
    session: SessionDep,
) -> TemplateSchemaOut:
    stmt = select(TemplateModel).where(TemplateModel.id == template_id)
    result = await session.execute(stmt)
    template = result.scalars().first()
    if not template:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=ClientErrorMessage.NOT_FOUND_TEMPLATE_ERROR.value
        )
    template.body = data.body
    session.add(template)
    await session.commit()
    await session.refresh(template)
    response = TemplateSchemaOut.model_validate(template, from_attributes=True)
    return response


@router.delete(path="/{template_id}", summary="Удалить шаблон")
async def delete_template(template_id: UUID4, session: SessionDep) -> Response:
    stmt = select(TemplateModel).where(TemplateModel.id == template_id)
    result = await session.execute(stmt)
    template = result.scalars().first()
    if not template:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=ClientErrorMessage.NOT_FOUND_TEMPLATE_ERROR.value
        )
    await session.delete(template)
    await session.commit()
    return Response(status_code=HTTP_204_NO_CONTENT)
