from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    temperature: float = 0.7

    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2023-12-01-preview"

    google_api_key: str | None = None

    history_max_size: int = 2048

    discord_bot_token: str
