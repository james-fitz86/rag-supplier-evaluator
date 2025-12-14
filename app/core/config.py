from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Multi-Agent Supplier RAG API"

    database_url: str = "postgresql+psycopg://rag_user:rag_password@db:5432/rag_db"

    # LLM config (for ExtractorAgent)
    openai_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(envfile=".env")


settings = Settings()

API_VERSION = "0.1.0"
API_NAME = "Multi-Agent RAG System"
API_DESCRIPTION = "Multi-Agent RAG System for Supplier Quotation Analysis"

DATABASE_URL = settings.database_url
