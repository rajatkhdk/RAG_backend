# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Settings:
#     REDIST_HOST = os.getenv("REDIS_HOST")
#     REDIS_PORT = int(os.getenv("REDIS_PORT"))

#     QDRANT_HOST = os.getenv("QDRANT_HOST")
#     QDRANT_PORT = int(os.getenv("QDRANT_PORT"))

#     DATABASE_URL = os.getenv("DATABASE_URL")

# settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # Database
    DATABASE_URL: str 

    # Grok api key
    GROK_API_KEY: str

    # load from .env automatically
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # class Config:
    #     extra = "allow"  # <--- allow extra fields in .env

settings = Settings()