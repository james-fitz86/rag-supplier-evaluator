from __future__ import annotations

from typing import Tuple, List, Optional

from app.agents.evaluator_agent import evaluate_offers
from app.schemas.query import OfferEvaluation


def evaluate_retrieved_offers(
    user_query: str,
    offers: List[OfferEvaluation],
    llm_client: Optional[object] = None,
) -> Tuple[str, str]:
    return evaluate_offers(user_query=user_query, offers=offers, llm_client=llm_client)
