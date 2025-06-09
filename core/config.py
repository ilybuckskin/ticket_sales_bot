from pydantic.v1 import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str

    model_config = ConfigDict(env_file=".env")


settings = Settings()
