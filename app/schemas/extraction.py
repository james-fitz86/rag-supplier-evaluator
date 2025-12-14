# app/schemas/extraction.py
from pydantic import BaseModel, Field
from typing import Optional

class ExtractedQuotation(BaseModel):
    supplier_name: str = Field(..., description="Supplier / company name")
    item_description: str = Field(..., description="What is being quoted")
    unit_price: float = Field(..., ge=0)
    currency: str = Field(default="EUR", description="ISO-ish currency code like EUR, USD, GBP")
    min_quantity: int = Field(default=1, ge=1)
    delivery_days: int = Field(..., ge=0)
    payment_terms: Optional[str] = None
    internal_note: Optional[str] = None
    risk_assessment: Optional[str] = None
