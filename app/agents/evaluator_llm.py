from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple, Set

import json

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
        "You MUST use only the provided offers. Do not invent details. "
        "Keep reasoning brief and reference price and delivery when available. "
        "If a required detail is missing from the offers, say it is unknown. "
        "Return a JSON object with keys: recommendation, reasoning."
    )

    offers_json = json.dumps(payload, ensure_ascii=False)

    user = (
        f"User request:\n{user_query}\n\n"
        f"Offers (JSON):\n{offers_json}\n\n"
        "Task:\n"
        "1) Choose the best supplier for the request.\n"
        "2) Base your decision only on the offers above.\n"
        "Output rules:\n"
        "- recommendation must exactly match one supplier string from the offers.\n"
        "- reasoning must be 1–3 sentences and cite specific offer fields (price and/or delivery_days).\n"
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
