"""Runtime configuration read from environment variables (and an optional .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE_URL = "https://main.d8gkeeaiko6qy.amplifyapp.com"

load_dotenv(PROJECT_ROOT / ".env")


class MissingCredentialsError(RuntimeError):
    """Raised when a test needs the Basic Auth credentials but they are not configured."""


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str

    def as_playwright(self) -> dict[str, str]:
        return {"username": self.username, "password": self.password}


@dataclass(frozen=True)
class Settings:
    base_url: str
    credentials: Credentials | None

    @classmethod
    def from_env(cls) -> Settings:
        username = os.getenv("APP_USERNAME")
        password = os.getenv("APP_PASSWORD")
        creds = Credentials(username, password) if username and password else None
        return cls(base_url=os.getenv("BASE_URL", DEFAULT_BASE_URL).rstrip("/"), credentials=creds)

    def require_credentials(self) -> Credentials:
        if self.credentials is None:
            raise MissingCredentialsError(
                "APP_USERNAME / APP_PASSWORD are not set. Copy .env.example to .env and fill them in."
            )
        return self.credentials
