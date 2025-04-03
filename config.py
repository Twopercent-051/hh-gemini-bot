import os

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

env_file = os.path.join(PROJECT_ROOT, ".env")

print(env_file)


class BotConfig(BaseSettings):
    bot_token: str
    admin_id: int
    debug: bool
    model_config = SettingsConfigDict(env_file=env_file, env_file_encoding="utf-8", extra="ignore")


class RedisConfig(BaseSettings):
    host: str
    port: int
    db: int
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="REDIS_",
    )


class HhConfig(BaseSettings):
    app_title: str
    client_id: str
    client_secret: str
    resume_id: str
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="HH_",
    )


class GeminiConfig(BaseSettings):
    api_key: str
    model_config = SettingsConfigDict(
        env_file=env_file,
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="GEMINI_",
    )


class Settings(BaseSettings):
    bot: BotConfig = BotConfig()  # type: ignore
    redis: RedisConfig = RedisConfig()  # type: ignore
    hh: HhConfig = HhConfig()  # type: ignore
    gemini: GeminiConfig = GeminiConfig()  # type: ignore


# Создание конфигурации
config = Settings()
