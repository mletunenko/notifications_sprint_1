from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import UUID4
from sqlalchemy import select
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from db.postgres import SessionDep
from models import TemplateModel
from schemas.templates import TemplateListParams, TemplateSchemaIn, TemplateSchemaOut
from utils.enums import ClientErrorMessage

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", summary="Получить список шаблонов", response_model=list[TemplateSchemaOut])
async def get_templates_list(
    session: SessionDep, query_params: TemplateListParams = Depends()
) -> list[TemplateModel]:
    stmt = select(TemplateModel)
    if query_params.body:
        like = f"%{query_params.body}%"
        stmt = stmt.filter(TemplateModel.body.ilike(like))
    result = await session.execute(stmt)
    template_list = list(result.scalars().all())
    return template_list


@router.get("/{template_id}", summary="Получить шаблон по id", response_model=TemplateSchemaOut)
async def get_template(template_id: UUID4, session: SessionDep) -> TemplateModel:
    stmt = select(TemplateModel).where(TemplateModel.id == template_id)
    result = await session.execute(stmt)
    template = result.scalars().first()
    if not template:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=ClientErrorMessage.NOT_FOUND_TEMPLATE_ERROR.value
        )
    return template


@router.post("", summary="Создать шаблон", response_model=TemplateSchemaOut)
async def create_template(data: TemplateSchemaIn, session: SessionDep) -> TemplateModel:
    new_template = TemplateModel(body=data.body)
    session.add(new_template)
    await session.commit()
    return new_template


@router.patch(path="/{template_id}", summary="Обновление шаблона", response_model=TemplateSchemaOut)
async def update_template(
    template_id: UUID4,
    data: TemplateSchemaIn,
    session: SessionDep,
) -> TemplateModel:
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
    return template


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
