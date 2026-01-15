# **Backend directory tree (expanded)**

```
backend/
├── app/
│   ├── init.py
│   ├── main.py
│   ├── api/
│   │   ├── init.py
│   │   └── endpoints/
│   │       ├── init.py
│   │       ├── qa.py                # POST /api/qa → {answer, context_summary, citations}
│   │       ├── ingredients.py       # GET /api/ingredients?search=...
│   │       ├── supplements.py       # GET /api/supplements?search=...
│   │       ├── products.py          # GET /api/products?search=...
│   │       ├── concerns.py          # GET /api/concerns
│   │       ├── interactions.py      # GET /api/interactions?entity_a=...&entity_b=...
│   │       └── export.py            # POST /api/export (CSV/PDF from payload)
│   ├── db/
│   │   ├── init.py
│   │   ├── models.py                # SQLAlchemy models: Ingredients, Supplements, Products,
│   │   │                             # Concerns, ConcernMappings, Interactions, Sources, Chunks
│   │   └── session.py               # engine/session helpers and init_db()
│   ├── core/
│   │   ├── init.py
│   │   ├── config.py                # env + paths (DB URL, data dirs, model IDs)
│   │   ├── prompts.py               # prompt builders
│   │   ├── rag_pipeline.py          # orchestrates: hybrid_retrieve -> compose -> generate
│   │   ├── hybrid_retrieve.py       # NEW: combine SQL facts + vector chunks
│   │   ├── index.py                 # vector index helpers (FAISS/Chroma/Lance)
│   │   ├── retrieve.py              # vector top-k retrieval
│   │   ├── rerank.py                # optional cross-encoder/LLM rerank
│   │   ├── compose.py               # build 300–500 token context summary + inline citations
│   │   └── generate.py              # LLM call (OpenRouter/other)
│   └── schemas/
│       ├── init.py
│       ├── ingredient.py            # response models for /ingredients
│       ├── supplement.py            # response models for /supplements
│       ├── product.py               # response models for /products
│       ├── concern.py               # response models for /concerns
│       ├── interaction.py           # response models for /interactions
│       ├── export.py                # request model for /export (rows → CSV/PDF)
│       └── qa.py                    # QARequest/QAResponse (+citations, context_summary)
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/                    # migration files for all tables above
├── scripts/
│   ├── etl.py                       # load/normalize public datasets → SQL tables
│   ├── seed_db.py                   # convenience seeding script
│   └── ingest_rag.py                # CSV/SQL → corpus.jsonl → embeddings → index
├── data/
│   ├── raw/                         # source CSVs (EU/CA datasets, etc.)
│   ├── processed/                   # corpus.jsonl (text/meta/emb)
│   └── index/                       # vector index files (if local)
├── tests/
│   ├── test_endpoints.py            # /ingredients, /supplements, /products, /qa smoke tests
│   ├── test_rag_pipeline.py
│   └── test_compose.py              # ensures summary length + citation IDs present
├── Dockerfile
├── docker-compose.yml               # FastAPI + MySQL + (optional) pgvector/chroma service
└── requirements.txt
```

# Descriptions

- `app/main.py`

  - FastAPI app factory. Wires endpoint routers under `/api`.
- `app/api/endpoints`

  - `qa.py` — POST /api/qa: accepts question (+ optional concern) and returns a structured response with `answer`, `context_summary`, and `citations` produced by the hybrid RAG pipeline.
  - `ingredients.py`, `supplements.py`, `products.py` — listing/search endpoints with query params and basic pagination.
  - `concerns.py` — returns taxonomy of concerns.
  - `interactions.py` — returns interactions between two entities (e.g., ingredient vs drug).
  - `export.py` — accepts rows and returns CSV/PDF export (placeholder endpoint; can return signed URL or file data).
- `app/db/models.py`

  - SQLAlchemy models representing domain entities and supporting the RAG corpus (Sources, Chunks).
- `app/db/session.py`

  - Creates SQLAlchemy engine & `SessionLocal`. Includes `init_db()` helper to create tables.
- `app/core`

  - `config.py` — pydantic-based settings: DB URL, data directories, model ids (embedding & LLM), and vector store choice.
  - `hybrid_retrieve.py` — combines high-precision SQL facts with vector store chunks (supports filters by concern/ingredient).
  - `compose.py` — composes a compact context summary (300–500 tokens) and returns inline citations.
  - `generate.py` — calls the LLM using the composed context; adheres to a context-only policy (no retrieval in LLM call).
  - `rag_pipeline.py` — orchestrates the full flow: hybrid_retrieve → compose_context → generate_answer.
- `alembic/` — placeholder migration environment; use `alembic` to generate and apply migrations for the SQL models.
- `scripts/`

  - `etl.py` — load & normalize CSVs into SQL tables.
  - `seed_db.py` — convenience script to seed demo/test data.
  - `ingest_rag.py` — create corpus JSONL from SQL/CSV, compute embeddings, and persist the vector index.
- `data/` — stores raw CSVs, processed corpus file, and local index files (if using a file-backed vector store).
- `tests/` — lightweight smoke tests and unit tests for composition behavior and the pipeline skeleton. Some endpoint tests are gated so they won't fail if FastAPI or other dependencies aren't installed in the environment.
- `Notes & next steps:`

  - The repository currently contains placeholder implementations for the RAG pipeline components and endpoints. To turn this into a runnable RAG service we will need to:
    - Use a vector store (FAISS / pgvector?) and implement `app/core/index.py` + `scripts/ingest_rag.py` to persist/load embeddings.
    - Choose an embedding model and LLM provider (configured in `app/core/config.py`) and implement `generate.py` to call the provider.
    - Implement `hybrid_retrieve.py` to combine SQL facts (high-precision) with vector chunk retrieval.
    - Create Alembic migrations and run `scripts/seed_db.py` to populate initial data.
