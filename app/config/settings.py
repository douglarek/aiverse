from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    temperature: float = 0.7

    google_api_key: str | None = None

    openai_log: str = "info"
    openai_organization: str | None = None
    openai_api_key: str | None = None
    openai_api_base: str | None = None
    openai_model_name: str = "gpt-3.5-turbo"

    mistral_api_key: str | None = None
    mistral_model: str = "mistral-small"

    history_max_size: int = 2000

    discord_bot_token: str = ""
    telegram_bot_token: str = ""
    telegram_allowed_users: list[str] = []

    openweathermap_api_key: str | None = None

    google_cse_id: str | None = None

    enable_wikipedia: bool = False

    enable_twitter_translator: bool = False

    groq_api_key: str | None = None
    groq_model: str = "mixtral-8x7b-32768"

    anthropic_api_key: str | None = None
    claude_model: str = "claude-3-opus-20240229"

    @property
    def is_openai(self) -> bool:
        return self.openai_api_key is not None

    @property
    def is_mistral(self) -> bool:
        return self.mistral_api_key is not None

    @property
    def is_google(self) -> bool:
        return self.google_api_key is not None

    @property
    def is_anthropic(self) -> bool:
        return self.anthropic_api_key is not None

    @property
    def enable_google_search(self) -> bool:
        return self.google_cse_id is not None and self.google_api_key is not None

    @property
    def enable_openweathermap(self) -> bool:
        return self.openweathermap_api_key is not None

    @property
    def is_groq(self) -> bool:
        return self.groq_api_key is not None
