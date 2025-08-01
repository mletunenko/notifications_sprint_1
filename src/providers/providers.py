import abc
import smtplib
from email.message import EmailMessage

import aiohttp
import backoff
from aiohttp import ClientConnectionError
from jinja2 import Template
from sqlalchemy import select

from core.config import settings
from db.postgres import new_session
from models.notifications import NotificationModel
from models.templates import TemplateModel
from utils.enums import NotificationMethodEnum


class AbstractProvider(abc.ABC):
    @abc.abstractmethod
    async def prepare_message(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def send_message(self):
        raise NotImplementedError


class EmailProvider(AbstractProvider):
    def __init__(self, template_id, profile_id, subject) -> None:
        self.template_id: str = template_id
        self.profile_id: str = profile_id
        self.subject: str = subject
        self.body: str = ""

    async def get_template(self, template_id: str) -> str:
        async with new_session() as pg_session:
            stmt = select(TemplateModel).where(TemplateModel.id == template_id)
            result = await pg_session.execute(stmt)
            template = result.scalars().first()
            assert template is not None
            return template.body

    @backoff.on_exception(backoff.expo, ClientConnectionError, max_time=15)
    async def get_context(self, profile_id: str) -> dict:
        context = {}
        url = f"http://{settings.profile_service.host}:{settings.profile_service.port}{settings.profile_service.profile_path}/{profile_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                context["first_name"] = data["first_name"]
        return context

    @backoff.on_exception(backoff.expo, ClientConnectionError, max_time=15)
    async def get_address(self, profile_id: str) -> str:
        url = (
            f"http://{settings.profile_service.host}:"
            f"{settings.profile_service.port}{settings.profile_service.profile_path}/{profile_id}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data["email"]

    async def prepare_message(self):
        template_str = await self.get_template(self.template_id)
        context = await self.get_context(self.profile_id)
        template = Template(template_str)
        self.body = template.render(context)

    async def send_message(self) -> None:
        # ! with ?
        server = smtplib.SMTP_SSL(settings.mail_transport.host, settings.mail_transport.port)
        server.login(settings.mail_transport.login, settings.mail_transport.password)

        address = await self.get_address(self.profile_id)
        message = EmailMessage()
        message["From"] = settings.mail_transport.email
        message["To"] = address
        message["Subject"] = self.subject
        message.add_alternative(self.body, subtype="html")

        try:
            server.sendmail(settings.mail_transport.email, [address], message.as_string())

            notification = NotificationModel(
                profile_id=self.profile_id,
                method=NotificationMethodEnum.EMAIL,
                address=address,
                subject=self.subject,
                content=self.body,
            )
            async with new_session() as pg_session:
                pg_session.add(notification)
                await pg_session.commit()

        finally:
            server.close()
