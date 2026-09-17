import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str
    cors_allowed_origin: list[str]


def get_settings() -> Settings:
    return Settings(
        DATABASE_URL=os.environ["DATABASE_URL"],
        cors_allowed_origin=[os.environ["CORS_ALLOWED_ORIGIN"]],
    )
