from sqlalchemy.orm import Session

from app.agents.retriever_agent import retrieve_quotations
from app.schemas.query import QueryResponse, OfferEvaluation
from app.services.evaluation_service import evaluate_retrieved_offers


def run_query(text: str, db: Session, top_k: int = 5, llm_client=None) -> QueryResponse:
    """
    Orchestrate the query workflow.

    Steps:
    - Generate an embedding for the query and retrieve the top-k most similar quotations (pgvector)
    - Map retrieved quotations into OfferEvaluation objects
    - Evaluate the offers to produce a recommendation and grounded reasoning
      - If an LLM client is available, use it
      - Otherwise fall back to a simple heuristic evaluator
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

    return QueryResponse(
        recommendation=recommendation,
        reasoning=reasoning,
        offers_evaluated=offers,
    )
