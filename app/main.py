from fastapi import FastAPI
from app.api.v1.routes import router as api_v1_router

app = FastAPI(title="Multi-Agent Supplier RAG API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Agent RAG API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_v1_router, prefix="/api/v1")

