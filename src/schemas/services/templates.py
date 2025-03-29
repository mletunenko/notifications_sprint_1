from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_404_NOT_FOUND

from models import TemplateModel
from schemas.templates import TemplateListParams, TemplateSchemaIn
from utils.enums import ClientErrorMessage


class TemplateService:
    @staticmethod
    async def get_templates_list(
        session: AsyncSession, query_params: TemplateListParams
    ) -> list[TemplateModel]:
        stmt = select(TemplateModel)
        if query_params.body:
            like = f"%{query_params.body}%"
            stmt = stmt.filter(TemplateModel.body.ilike(like))
        result = await session.execute(stmt)
        template_list = list(result.scalars().all())
        return template_list

    @staticmethod
    async def get_template(template_id: UUID4, session: AsyncSession) -> TemplateModel:
        stmt = select(TemplateModel).where(TemplateModel.id == template_id)
        result = await session.execute(stmt)
        template = result.scalars().first()
        if not template:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND, detail=ClientErrorMessage.NOT_FOUND_TEMPLATE_ERROR.value
            )
        return template

    @staticmethod
    async def create_template(data: TemplateSchemaIn, session: AsyncSession) -> TemplateModel:
        new_template = TemplateModel(body=data.body)
        session.add(new_template)
        await session.commit()
        return new_template

    @staticmethod
    async def update_template(
        template_id: UUID4, data: TemplateSchemaIn, session: AsyncSession
    ) -> TemplateModel:
        template = await TemplateService.get_template(template_id, session)
        template.body = data.body
        session.add(template)
        await session.commit()
        return template

    @staticmethod
    async def delete_template(template_id: UUID4, session: AsyncSession) -> None:
        template = await TemplateService.get_template(template_id, session)
        await session.delete(template)
        await session.commit()
