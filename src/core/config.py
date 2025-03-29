from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8005


class DatabaseConfig(BaseModel):
    url: str = "postgresql+asyncpg://user:password@127.0.0.1:30002/notifications"
    sync_url: str = "postgresql+psycopg://user:password@auth_postgres:30002/notifications"
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class LogstashConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5044


class MailTransportSettings(BaseModel):
    host: str = "smtp.yandex.ru"
    port: int = 465
    domain: str = "yandex.ru"
    login: str = "marialetunenko"
    password: str = "elzurvjrhqtjoqud"

    @property
    def email(self):
        return f"{self.login}@{self.domain}"


class Settings(BaseSettings):
    model_config = ConfigDict(  # type: ignore
        env_file=(".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig = DatabaseConfig()
    logstash: LogstashConfig = LogstashConfig()
    sentry_enable: bool = True
    sentry_sdk: str
    queue_host: str = "localhost"

    mail_transport: MailTransportSettings = MailTransportSettings()
    auth_host: str = "127.0.0.1"
    auth_port: str = "8000"
    user_path: str = "/auth/users"
    user_list_path: str = "/autn/users"


settings = Settings()
