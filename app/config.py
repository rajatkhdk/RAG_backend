import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    REDIST_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = int(os.getenv("REDIS_PORT"))

    QDRANT_HOST = os.getenv("QDRANT_HOST")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT"))

    DATABASE_URL = os.getenv("DATABASE_URL")

setting = Settings()