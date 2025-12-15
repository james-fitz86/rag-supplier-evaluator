# Multi-Agent RAG System for Supplier Quotation Evaluation

## Overview

This project implements a **multi-agent Retrieval-Augmented Generation (RAG) system** designed to ingest supplier quotations, retrieve the most relevant offers using vector similarity search, and evaluate them to recommend the best supplier based on a natural-language user query.

The system follows a **modular, agent-based architecture** with clear separation of concerns and graceful degradation when external LLM services are unavailable.

This repository includes **all source code and Docker configuration required to download, run, and test the system locally**, as required by the take-home task.

---

## Architecture Summary

The system is composed of the following core agents and services:

### Agents
- **ExtractorAgent** – Uses an LLM to extract structured commercial data from raw supplier quotations.
- **RetrieverAgent** – Retrieves relevant quotations using pgvector cosine similarity.
- **EvaluatorAgent**
  - Primary path: LLM-based, grounded evaluation over retrieved offers.
  - Fallback path: Deterministic scoring based on constraints, price, delivery, and risk.
- **SummarizerAgent** (optional) – Produces a concise post-evaluation summary using an LLM, with a deterministic fallback.

### Services
- **Ingestion Service** – Handles quotation ingestion, extraction, embedding generation, and persistence.
- **Query Service** – Orchestrates retrieval, evaluation, and summarization.
- **Evaluation Service** – Provides a clean seam between query orchestration and evaluator logic.

### Storage & Infrastructure
- **PostgreSQL + pgvector** for embeddings and similarity search
- **FastAPI** for the API layer
- **Docker & Docker Compose** for local development and testing

---

## High-Level Flow

```text
Upload Quotation
      ↓
ExtractorAgent (LLM)
      ↓
Store structured data + embeddings
      ↓
User Query
      ↓
RetrieverAgent (vector similarity)
      ↓
EvaluatorAgent
   ├─ LLM reasoning (if available)
   └─ Deterministic scoring fallback
      ↓
SummarizerAgent (optional)
      ↓
API Response
```

## API Endpoints

### POST /api/v1/upload

Ingest a raw supplier quotation.

Behaviour:
- Extract structured fields using an LLM
- Generate embeddings
- Store quotation in the database

Request Body:
```json
{
  "text": "Supplier SteelWorks Ltd offers 10mm steel bolts (SB-10) at a unit price of 0.82 EUR. No minimum order quantity applies. Delivery is guaranteed within 5 days. Payment terms are Net 15. Internal note: Premium supplier with excellent quality and a strong history of on-time delivery."
}
```

### POST /api/v1/query

#### Example 1: Delivery-Constrained Query (LLM Enabled)

Query the system using natural language to receive a supplier recommendation.

Expected Behaviour:
- RetrieverAgent returns relevant quotations
- EvaluatorAgent selects a supplier that satisfies the delivery constraint
- SummarizerAgent prepends a concise summary

Request Body:
```json
{
  "query": "Need 10mm steel bolts delivered within 7 days"
}
```
Response Body:
```json
{
  "recommendation": "SteelWorks Ltd",
  "reasoning": "The decision to choose SteelWorks Ltd matches the request as they offer delivery within 5 days.\n\nSteelWorks Ltd offers the best balance of delivery time and price based on the retrieved offers.",
  "offers_evaluated": []
}
```

#### Example 2: Same Query Without LLM (Fallback Behaviour)

When the OpenAI API key is not configured:

Expected Behaviour:
- Deterministic evaluator scoring is used
- Deterministic summary is generated
- System remains fully operational

Example response:
```json
{
  "recommendation": "SteelWorks Ltd",
  "reasoning": "Recommended SteelWorks Ltd based on the retrieved offers and request constraints.\n\nSelected SteelWorks Ltd using deterministic scoring based on delivery compliance and price.",
  "offers_evaluated": [...]
}
```

### GET /api/v1/version

Returns basic API version metadata.

### LLM-Based Evaluation

When an OpenAI API key is configured:
- The evaluator reasons over retrieved offers only
- The model is constrained to return strict JSON
- Recommendations are validated against retrieved supplier names

### Deterministic Fallback Evaluation

When the LLM is unavailable or fails:
- Constraints are extracted from the user query
- Offers are scored based on:
  - Delivery compliance
  - Unit price
  - Risk indicators
- A ranked, explainable recommendation is produced

This ensures the system remains operational without external dependencies.

## Summarizer Agent

The optional SummarizerAgent runs after evaluation and:
- Produces a short, user-friendly summary of the decision
- Uses an LLM when available
- Falls back to a deterministic summary when the LLM is unavailable

The summary is prepended to the evaluator’s detailed reasoning.

## Docker Setup and Local Testing

### Prerequisites

- Docker and Docker Compose installed
- (Optional) OpenAI API key for LLM-powered extraction, evaluation, and summarization

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/james-fitz86/rag-supplier-evaluator.git
cd rag-supplier-evaluator
```

2. Create a .env file and set environment variables:
```bash
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=rag_password
POSTGRES_DB=rag_db
OPENAI_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o-mini
DATABASE_URL=postgresql+psycopg://user:password@db:5432/app
```

3. Build and start the services:

```bash
docker-compose up --build
```

Once running, the API is available at:

http://localhost:8000

Interactive API documentation (Swagger UI):

http://localhost:8000/docs

If OPENAI_API_KEY is not set, the system automatically falls back to deterministic evaluation and summarization.

## Verification and Testing

The following behaviours were manually verified:
- Successful quotation ingestion and extraction
- Correct vector-based retrieval of relevant offers
- LLM-based evaluation prioritising query constraints
- Deterministic scoring fallback when the LLM is disabled
- SummarizerAgent functioning with and without LLM access

Screenshots of API responses and database checks are included in the repository.

## Design Rationale

The system prioritises:
- Explainability over opaque recommendations
- Reliability through deterministic fallbacks
- Clear agent separation for extensibility
- Production-style robustness against external dependency failure

This architecture closely mirrors real-world decision-support systems.

## Known Limitations

- Query constraint extraction is rule-based and limited to common patterns
- Deterministic scoring weights are static and not configurable
- No automated unit or integration tests are included
- Evaluation currently assumes all retrieved offers are comparable
- No frontend UI is provided; interaction is via API only

## Future Improvements / Next Steps

- Add configurable weighting for evaluation criteria
- Expand constraint parsing for more complex queries
- Introduce automated test coverage
- Add asynchronous evaluation for higher throughput
- Build a simple frontend UI for interactive querying
- Support batch queries and multi-item requests

## Repository Contents

This repository includes:

- Full FastAPI source code
- Agent-based RAG architecture implementation
- PostgreSQL + pgvector setup
- Docker and Docker Compose configuration
- Example API usage via Swagger
- Screenshots demonstrating system behaviour

All components required to download, run, and test the system locally are included.
