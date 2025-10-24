from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str = Field(description="DB user name")
    POSTGRES_PASSWORD: str = Field(description="DB password")
    POSTGRES_DB: str = Field(description="DB database name")

    APP_ENVIRONMENT: str = Field(description="Environment name")

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
