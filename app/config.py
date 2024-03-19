from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Config
    app_name: str

    # JWT Config
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    # Database Config
    main_database_url: str
    test_database_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()