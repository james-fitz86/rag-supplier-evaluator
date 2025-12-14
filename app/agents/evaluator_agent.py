from __future__ import annotations

from typing import Iterable, Tuple, Optional

from app.agents.evaluator_llm import evaluate_with_llm


def _heuristic_pick(offers_list: list[object]) -> Tuple[str, str]:
    def sort_key(o: object) -> tuple:
        price = getattr(o, "unit_price", None)
        days = getattr(o, "delivery_days", None)

        price_key = price if price is not None else float("inf")
        days_key = days if days is not None else float("inf")
        return (price_key, days_key)

    best = sorted(offers_list, key=sort_key)[0]

    supplier = getattr(best, "supplier", "Unknown")
    price = getattr(best, "unit_price", None)
    days = getattr(best, "delivery_days", None)

    reasoning = (
        "Selected the lowest unit price from the retrieved offers. "
        f"Chosen supplier={supplier}, unit_price={price}, delivery_days={days}."
    )
    return supplier, reasoning


def evaluate_offers(
    user_query: str,
    offers: Iterable[object],
    llm_client: Optional[object] = None,
) -> Tuple[str, str]:
    """
    Evaluator (wired):
    - If llm_client is available, use LLM-based evaluation (grounded on retrieved offers)
    - Otherwise fall back to simple heuristic
    """
    offers_list = list(offers)
    if not offers_list:
        return ("No match", "No offers were retrieved to evaluate.")

    if llm_client is not None:
        try:
            return evaluate_with_llm(user_query=user_query, offers=offers_list, llm_client=llm_client)
        except Exception:
            # Guardrail: any LLM failure falls back to deterministic logic
            return _heuristic_pick(offers_list)

    return _heuristic_pick(offers_list)
