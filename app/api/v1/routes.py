from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.upload import UploadRequest, UploadResponse
from app.schemas.query import QueryRequest, QueryResponse, OfferEvaluation
from app.schemas.version import VersionResponse
from app.core.config import API_VERSION, API_NAME, API_DESCRIPTION
from app.core.db import get_db
from app.services.ingestion_service import ingest_quotation
from app.services.query_service import run_query
from app.core.llm_client import build_llm_client, LLMClientError

router = APIRouter()


def get_llm_client():
    try:
        return build_llm_client()
    except LLMClientError as e:
        raise HTTPException(status_code=501, detail=str(e))


@router.post("/upload", response_model=UploadResponse)
def upload_quotation(
    payload: UploadRequest,
    db: Session = Depends(get_db),
    llm_client=Depends(get_llm_client),
) -> UploadResponse:
    """
    Ingest a raw supplier quotation.

    Behaviour:
    - Extract structured fields via ExtractorAgent (requires configured LLM client)
    - Generate an embedding vector
    - Store quotation in the database
    - Return the new quotation ID and a confirmation message
    """
    quotation = ingest_quotation(payload.text, db, llm_client)

    return UploadResponse(
        id=quotation.id,
        message="Quotation ingested successfully",
    )


@router.post("/query", response_model=QueryResponse)
def query_text(
    payload: QueryRequest,
    db: Session = Depends(get_db),
) -> QueryResponse:
    """
    Query the system with a natural language request.

    Current behaviour:
    - Retrieve top-k quotations using vector similarity
    - Return them in the expected response shape

    Later:
    - Run EvaluatorAgent to produce a grounded recommendation and reasoning
    """
    return run_query(payload.query, db=db, top_k=5)


@router.get("/version", response_model=VersionResponse, tags=["meta"])
def get_version() -> VersionResponse:
    """
    Return basic API version metadata.
    """
    return VersionResponse(
        version=API_VERSION,
        name=API_NAME,
        description=API_DESCRIPTION,
    )
