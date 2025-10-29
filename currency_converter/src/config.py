from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class containing all environment variables and methods for database url generation"""

    DB_USER: str = Field(description="DB user name")
    DB_PASS: str = Field(description="DB password")
    DB_NAME: str = Field(description="DB database name")
    DB_HOST_PORT: int = Field()

    APP_ENVIRONMENT: Literal["DOCKER", "LOCAL"] = "LOCAL"

    EXTERNAL_API_URL: str = Field(description="Base URL for API calls")

    TIMEZONE: str = Field(description="Timezone used by the application")

    NATIONAL_CURRENCY: str = Field(description="National currency code")

    @property
    def database_url(self):
        # db is a name of postgres image in compose.yaml file
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@db:5432/{self.DB_NAME}"
        )

    @property
    def local_database_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@localhost:{self.DB_HOST_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
