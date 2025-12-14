from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple, Set


def evaluate_with_llm(
    user_query: str,
    offers: Iterable[object],
    llm_client: object,
) -> Tuple[str, str]:
    """
    Use the LLM to select the best supplier using ONLY the retrieved offers.

    Expects llm_client to provide:
        chat_json(system: str, user: str) -> dict
    """
    offers_list = list(offers)
    suppliers: Set[str] = set()

    payload = []
    for o in offers_list:
        supplier = getattr(o, "supplier", None) or "Unknown"
        suppliers.add(supplier)
        payload.append(
            {
                "supplier": supplier,
                "item": getattr(o, "item", None),
                "unit_price": getattr(o, "unit_price", None),
                "delivery_days": getattr(o, "delivery_days", None),
                "risk_assessment": getattr(o, "risk_assessment", None),
            }
        )

    system = (
        "You are an evaluation agent for supplier quotations. "
        "You MUST use only the provided offers. "
        "Do not invent details. "
        "Return a JSON object with keys: recommendation, reasoning."
    )

    user = (
        f"User request:\n{user_query}\n\n"
        f"Offers:\n{payload}\n\n"
        "Choose the best supplier. "
        "recommendation must exactly match one of the supplier names in the offers."
    )

    # The OpenAIJsonClient already forces JSON and parses it for us.
    data: Dict[str, Any] = llm_client.chat_json(system=system, user=user)  # type: ignore[attr-defined]

    recommendation = (data.get("recommendation") or "").strip()
    reasoning = (data.get("reasoning") or "").strip()

    if not recommendation:
        raise ValueError("LLM returned empty recommendation.")
    if recommendation not in suppliers:
        raise ValueError("LLM recommendation not in retrieved supplier set.")
    if not reasoning:
        reasoning = "LLM returned no reasoning."

    return recommendation, reasoning
