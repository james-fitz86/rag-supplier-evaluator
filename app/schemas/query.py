from typing import List
from pydantic import BaseModel

class OfferEvaluation(BaseModel):
    supplier: str
    item: str
    unit_price: float
    delivery_days: int
    risk_assessment: str

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    recommendation: str
    reasoning: str
    offers_evaluated: List[OfferEvaluation]
