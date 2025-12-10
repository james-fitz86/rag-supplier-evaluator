from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Multi-Agent Supplier RAG API"

    class Config:
        env_file = ".env"

settings = Settings()
