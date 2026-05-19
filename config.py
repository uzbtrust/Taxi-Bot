from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    api_id: int
    api_hash: str
    fernet_key: str
    admin_ids: str = ""
    user_ids: str = ""
    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        import os
        if os.path.isdir("/data"):
            return "sqlite+aiosqlite:////data/taxi_bot.db"
        return "sqlite+aiosqlite:///./taxi_bot.db"

    @property
    def admin_id_list(self) -> list[int]:
        return [int(i.strip()) for i in self.admin_ids.split(",") if i.strip()]

    @property
    def user_id_list(self) -> list[int]:
        return [int(i.strip()) for i in self.user_ids.split(",") if i.strip()]

    @property
    def allowed_ids(self) -> set[int]:
        return set(self.admin_id_list + self.user_id_list)


settings = Settings()
