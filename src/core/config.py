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

    naming_conventions: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class LogstashConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 5044


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
    sentry_sdk: str = (
        "https://21ebc037b0d0f712c4cd5e246511459b@o4508946947702784.ingest.us.sentry.io/4508946960875520"
    )


settings = Settings()
