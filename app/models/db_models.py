from typing import List

from sqlalchemy import String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.core.db import Base
from app.core.embeddings import EMBEDDING_DIM

class Quotation(Base):
    __tablename__ = "quotations"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Structured commercial information
    supplier_name: Mapped[str] = mapped_column(String(100), index=True)
    item_description: Mapped[str] = mapped_column(Text)
    unit_price: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="EUR")
    min_quantity: Mapped[int] = mapped_column(Integer, default=1)
    delivery_days: Mapped[int] = mapped_column(Integer)
    payment_terms: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Internal supplier history / notes
    internal_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Store the original quotation text for auditability + RAG retrieval
    raw_text: Mapped[str] = mapped_column(Text)

    # Embedding vector used for similarity search
    embedding: Mapped[List[float]] = mapped_column(Vector(EMBEDDING_DIM))
