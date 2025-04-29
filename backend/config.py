from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "lizasecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10

    class Config:
        env_file = ".env"

settings = Settings()