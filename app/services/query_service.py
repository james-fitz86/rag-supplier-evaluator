from sqlalchemy.orm import Session

from app.agents.retriever_agent import retrieve_quotations
from app.schemas.query import QueryResponse, OfferEvaluation
from app.services.evaluation_service import evaluate_retrieved_offers
from app.agents.summarizer_agent import summarize_decision


def run_query(text: str, db: Session, top_k: int = 5, llm_client=None) -> QueryResponse:
    """
    Orchestrate the query workflow.

    Steps:
    - Retrieve top-k most similar quotations (pgvector similarity search)
    - Map retrieved quotations into OfferEvaluation objects
    - Evaluate offers to produce recommendation + reasoning (LLM if available, fallback otherwise)
    - Generate a brief summary and prepend it to the reasoning
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

    recommendation, reasoning = evaluate_retrieved_offers(
        user_query=text,
        offers=offers,
        llm_client=llm_client,
    )

    summary = summarize_decision(
        user_query=text,
        recommendation=recommendation,
        offers=offers,
        llm_client=llm_client,
    )

    if summary:
        reasoning = f"{summary}\n\n{reasoning}"

    return QueryResponse(
        recommendation=recommendation,
        reasoning=reasoning,
        offers_evaluated=offers,
    )
