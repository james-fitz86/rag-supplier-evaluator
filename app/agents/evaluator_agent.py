from __future__ import annotations

from typing import Iterable, Tuple, Optional

from app.agents.evaluator_llm import evaluate_with_llm
from app.agents.evaluator_scoring import pick_best_offer


def evaluate_offers(
    user_query: str,
    offers: Iterable[object],
    llm_client: Optional[object] = None,
) -> Tuple[str, str]:
    """
    Evaluator:
    - If llm_client is available, use LLM-based evaluation (grounded on retrieved offers)
    - Otherwise fall back to deterministic scoring (constraint + risk + price + delivery)
    """
    offers_list = list(offers)
    if not offers_list:
        return ("No match", "No offers were retrieved to evaluate.")

    if llm_client is not None:
        try:
            return evaluate_with_llm(user_query=user_query, offers=offers_list, llm_client=llm_client)
        except Exception:
            # Any LLM failure -> deterministic fallback
            return pick_best_offer(user_query=user_query, offers=offers_list)

    return pick_best_offer(user_query=user_query, offers=offers_list)
