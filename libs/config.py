from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    temperature: float = 0.7

    azure_openai_api_key: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str = "2023-12-01-preview"

    google_api_key: str | None = None

    azure_dalle_api_key: str | None = None
    azure_dalle_endpoint: str | None = None
    azure_dalle_deployment: str | None = None
    azure_dalle_api_version: str = "2023-12-01-preview"

    history_max_size: int = 2048

    discord_bot_token: str = ""
    telegram_bot_token: str = ""
    telegram_allowed_users: list[str] = []

    openweathermap_api_key: str | None = None

    google_cse_id: str | None = None

    enable_wikipedia: bool = False

    @property
    def is_azure(self) -> bool:
        return (
            self.azure_openai_api_key is not None
            and self.azure_openai_endpoint is not None
            and self.azure_openai_deployment is not None
        )

    @property
    def is_google(self) -> bool:
        return self.google_api_key is not None

    @property
    def has_vision(self) -> bool:
        return self.google_api_key is not None

    @property
    def has_dalle(self) -> bool:
        return (
            self.azure_dalle_api_key is not None
            and self.azure_dalle_endpoint is not None
            and self.azure_dalle_deployment is not None
        )

    @property
    def enable_google_search(self) -> bool:
        return self.google_cse_id is not None and self.google_api_key is not None

    @property
    def enable_openweathermap(self) -> bool:
        return self.openweathermap_api_key is not None
