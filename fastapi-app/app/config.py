from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


@lru_cache
class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    APP_ENV: str = Field(default="local")
    APP_NAME: str


settings = Setting()
