from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple, List


@dataclass(frozen=True)
class Constraints:
    max_delivery_days: Optional[int] = None
    max_unit_price: Optional[float] = None


def extract_constraints(user_query: str) -> Constraints:
    """
    Extract lightweight constraints from the user query.

    Supports patterns like:
    - "within 7 days", "under 10 days", "max 5 days", "no more than 3 days"
    - "under 0.80", "max €0.75", "below $1.20", "no more than 1.00"
    """
    text = user_query.lower()

    max_days: Optional[int] = None
    day_patterns = [
        r"(?:within|under|below|max(?:imum)?|no more than|at most)\s+(\d+)\s*(?:day|days)",
        r"(\d+)\s*(?:day|days)\s*(?:or less|or fewer|max(?:imum)?|at most)",
    ]
    for pat in day_patterns:
        m = re.search(pat, text)
        if m:
            try:
                max_days = int(m.group(1))
                break
            except ValueError:
                pass

    max_price: Optional[float] = None
    price_patterns = [
        r"(?:under|below|max(?:imum)?|no more than|at most)\s*[€$£]?\s*(\d+(?:\.\d+)?)",
        r"[€$£]\s*(\d+(?:\.\d+)?)\s*(?:or less|max(?:imum)?|at most)",
    ]
    for pat in price_patterns:
        m = re.search(pat, text)
        if m:
            try:
                max_price = float(m.group(1))
                break
            except ValueError:
                pass

    return Constraints(max_delivery_days=max_days, max_unit_price=max_price)


def risk_penalty(risk_text: str) -> float:
    """
    Convert free-text risk into a numeric penalty.
    Higher penalty = worse.
    """
    t = (risk_text or "").lower()

    if any(k in t for k in ["high risk", "unreliable", "frequent delays", "poor", "issues", "problem"]):
        return 2.0
    if any(k in t for k in ["medium risk", "moderate", "mixed"]):
        return 1.0
    if any(k in t for k in ["low risk", "reliable", "on-time", "trusted", "excellent"]):
        return -0.5

    return 0.0


def score_offer(
    unit_price: Optional[float],
    delivery_days: Optional[int],
    risk_assessment: str,
    constraints: Constraints,
) -> float:
    """
    Score an offer (higher is better).

    Principles:
    - Lower price and faster delivery score higher
    - Violating an explicit constraint gets a strong penalty
    - Risk text applies penalty
    """
    score = 0.0

    # Price contribution
    if unit_price is not None:
        score += 1.0 / max(unit_price, 0.0001)
        if constraints.max_unit_price is not None and unit_price > constraints.max_unit_price:
            score -= 3.0
    else:
        score -= 0.25

    # Delivery contribution
    if delivery_days is not None:
        score += 1.0 / max(float(delivery_days), 0.5)
        if constraints.max_delivery_days is not None and delivery_days > constraints.max_delivery_days:
            score -= 3.0
    else:
        score -= 0.25

    # Risk contribution
    score -= risk_penalty(risk_assessment)

    return score


def pick_best_offer(user_query: str, offers: Iterable[object]) -> Tuple[str, str]:
    """
    Deterministic evaluator:
    - extract constraints from user_query
    - score each offer
    - pick best
    - return (recommendation, reasoning) with a short top-3 summary
    """
    offers_list = list(offers)
    if not offers_list:
        return ("No match", "No offers were retrieved to evaluate.")

    constraints = extract_constraints(user_query)

    scored: List[Tuple[float, object]] = []
    for o in offers_list:
        s = score_offer(
            unit_price=getattr(o, "unit_price", None),
            delivery_days=getattr(o, "delivery_days", None),
            risk_assessment=getattr(o, "risk_assessment", "") or "",
            constraints=constraints,
        )
        scored.append((s, o))

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best = scored[0]

    best_supplier = getattr(best, "supplier", "Unknown")

    lines: List[str] = []
    lines.append(f"Selected **{best_supplier}** from the retrieved offers using deterministic scoring.")
    if constraints.max_delivery_days is not None:
        lines.append(f"Detected delivery constraint: ≤ {constraints.max_delivery_days} days.")
    if constraints.max_unit_price is not None:
        lines.append(f"Detected unit price constraint: ≤ {constraints.max_unit_price:g}.")

    lines.append("Top evaluated offers:")
    for idx, (s, o) in enumerate(scored[: min(3, len(scored))], start=1):
        supplier = getattr(o, "supplier", "Unknown")
        item = getattr(o, "item", "")
        unit_price = getattr(o, "unit_price", None)
        delivery_days = getattr(o, "delivery_days", None)
        risk = (getattr(o, "risk_assessment", "") or "").strip()
        lines.append(
            f"{idx}. {supplier} — unit_price={unit_price}, delivery_days={delivery_days}, risk='{risk}'"
            + (f", item='{item}'" if item else "")
        )

    return best_supplier, "\n".join(lines)
