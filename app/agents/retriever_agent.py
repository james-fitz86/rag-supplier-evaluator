from typing import List
from sqlalchemy.orm import Session

from app.models.db_models import Quotation
from app.core.embeddings import generate_embedding


def retrieve_quotations(query: str, db: Session, top_k: int = 5) -> List[Quotation]:
    """
    Retrieve the most relevant quotations using vector similarity search.
    Uses pgvector distance ordering on the embedding column.
    """
    query_vec = generate_embedding(query)

    # pgvector SQLAlchemy helpers expose distance functions on the Vector column
    results = (
        db.query(Quotation)
        .order_by(Quotation.embedding.cosine_distance(query_vec))
        .limit(top_k)
        .all()
    )

    return results
