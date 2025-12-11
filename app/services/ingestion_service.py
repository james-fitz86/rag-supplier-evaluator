from sqlalchemy.orm import Session

from app.models.db_models import Quotation
from app.core.embeddings import generate_embedding


def ingest_quotation(text: str, db: Session) -> Quotation:
    """
    Ingest a raw quotation text:
    - generate an embedding
    - (later) extract structured fields with an ExtractorAgent
    - store everything in the quotations table
    """

    embedding = generate_embedding(text)

    # TODO  replace these placeholder values with real extraction
    quotation = Quotation(
        supplier_name="Unknown",
        item_description=text[:2000],
        unit_price=0.0,
        currency="EUR",
        min_quantity=1,
        delivery_days=0,
        payment_terms=None,
        internal_note=None,
        risk_assessment=None,
        raw_text=text,
        embedding=embedding,
    )

    db.add(quotation)
    db.commit()
    db.refresh(quotation)
    return quotation
