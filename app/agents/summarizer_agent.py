from __future__ import annotations

from typing import Any, Dict, Iterable, Optional


def summarize_decision(
    user_query: str,
    recommendation: str,
    offers: Iterable[object],
    llm_client: Optional[object] = None,
) -> str:
    offers_list = list(offers)

    # No LLM? Just return the existing reasoning-friendly summary.
    if llm_client is None:
        return f"Recommended {recommendation} based on the retrieved offers and request constraints."

    payload = [
        {
            "supplier": getattr(o, "supplier", None),
            "unit_price": getattr(o, "unit_price", None),
            "delivery_days": getattr(o, "delivery_days", None),
            "risk_assessment": getattr(o, "risk_assessment", None),
        }
        for o in offers_list
    ]

    system = (
        "You are a summarization agent. Use only the provided offers and decision. "
        "Return JSON: {\"summary\": \"...\"}. Keep it 1-2 sentences."
    )
    user = (
        f"User request: {user_query}\n"
        f"Decision: {recommendation}\n"
        f"Offers: {payload}\n"
        "Summarize why the decision matches the request."
    )

    data: Dict[str, Any] = llm_client.chat_json(system=system, user=user)
    return (data.get("summary") or "").strip() or f"Recommended {recommendation} based on the retrieved offers."
