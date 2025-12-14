from sqlalchemy.orm import Session

from app.agents.retriever_agent import retrieve_quotations
from app.schemas.query import QueryResponse, OfferEvaluation


def run_query(text: str, db: Session, top_k: int = 5) -> QueryResponse:
    """
    Orchestrate the query workflow:
    - retrieve relevant quotations from DB (vector similarity)
    - map them into the response schema
    - (later) call EvaluatorAgent to pick best supplier + grounded reasoning
    """
    retrieved = retrieve_quotations(query=text, db=db, top_k=top_k)

    offers = [
        OfferEvaluation(
            supplier=q.supplier_name,
            item=q.item_description,
            unit_price=q.unit_price,
            delivery_days=q.delivery_days,
            risk_assessment=q.risk_assessment or "",
        )
        for q in retrieved
    ]

    # Placeholder until EvaluatorAgent exists
    recommendation = offers[0].supplier if offers else "No match"
    reasoning = (
        "Retrieved the most relevant offers from the database using vector similarity search. "
        "Evaluation agent not implemented yet."
    )

    return QueryResponse(
        recommendation=recommendation,
        reasoning=reasoning,
        offers_evaluated=offers,
    )
