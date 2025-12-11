from fastapi import FastAPI
from app.api.v1.routes import router as api_v1_router
from app.core.db import Base, engine, init_db
from app.models import db_models

app = FastAPI(title="Multi-Agent Supplier RAG API")

@app.on_event("startup")
def on_startup():
    init_db()
    Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Agent RAG API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_v1_router, prefix="/api/v1")

