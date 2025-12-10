from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Multi-Agent Supplier RAG API"

    model_config = SettingsConfigDict(envfile=".env")

settings = Settings()

API_VERSION = "0.1.0"
API_NAME = "Multi-Agent RAG System"
API_DESCRIPTION = "Multi-Agent RAG System for Supplier Quotation Analysis"
