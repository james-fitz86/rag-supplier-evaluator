from sqlalchemy.orm import Session

from app.models.db_models import Quotation
from app.core.embeddings import generate_embedding, EMBEDDING_DIM
from app.agents.extractor_agent import extract_quotation


def ingest_quotation(text: str, db: Session, llm_client) -> Quotation:
    """
    Ingest a raw quotation text:
    - extract structured fields using ExtractorAgent
    - generate an embedding
    - store everything in the quotations table
    """

    extracted = extract_quotation(llm_client, text)

    embedding = generate_embedding(text)
    if len(embedding) != EMBEDDING_DIM:
        raise ValueError(f"Embedding dim mismatch: got {len(embedding)} expected {EMBEDDING_DIM}")

    quotation = Quotation(
        supplier_name=extracted.supplier_name,
        item_description=extracted.item_description,
        unit_price=extracted.unit_price,
        currency=extracted.currency or "EUR",
        min_quantity=extracted.min_quantity or 1,
        delivery_days=extracted.delivery_days,
        payment_terms=extracted.payment_terms,
        internal_note=extracted.internal_note,
        risk_assessment=extracted.risk_assessment,
        raw_text=text,
        embedding=embedding,
    )

    db.add(quotation)
    db.commit()
    db.refresh(quotation)
    return quotation
