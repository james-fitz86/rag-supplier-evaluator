from fastapi import FastAPI

app = FastAPI(title="Multi-Agent Supplier RAG API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Multi-Agent RAG API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
