from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file = ".env", env_file_encoding = "utf-8"
    )
    
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_PORT: int
    DB_NAME: str
    DATABASE_URL: str