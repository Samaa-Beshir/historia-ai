# Historia AI

A Retrieval-Augmented Generation (RAG) application for exploring Egyptian
history through primary-source books and research papers, via a chat
interface with an era ("Time Travel") filter.

## Architecture

- **API layer** (`backend/app/api`): FastAPI routes + Pydantic schemas. Validation and routing only.
- **Service layer** (`backend/app/services`): orchestrates chat and document use cases.
- **AI layer** (`backend/app/ai`): embeddings, retrieval, prompt building, LLM provider.
- **Data layer** (`backend/app/data`): ChromaDB and metadata.csv repositories.
- **Frontend** (`frontend`): Next.js (App Router) + TypeScript + Tailwind + Zustand.

Pipeline: `Raw PDFs → metadata.csv → cleaned chunks → embeddings → ChromaDB → retrieval → prompt → LLM → response`.

## Prerequisites

- Python 3.11+
- Node.js 20+
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)

## First-time setup

### 1. Configure environment

```bash
cp .env.example .env
# edit .env and set GEMINI_API_KEY
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Windows
# source .venv/bin/activate && pip install -r requirements.txt   # macOS/Linux

# Build the document catalog and vector index (run once, or after adding new PDFs to data/row)
.venv\Scripts\python -m app.scripts.build_metadata
.venv\Scripts\python -m app.scripts.build_chunks
.venv\Scripts\python -m app.scripts.ingest

# Run the API
.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Run tests: `.venv\Scripts\python -m pytest`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Adding more documents

Drop new PDFs into `data/row/<books|research_papers>/<Era_Name>/`, then
re-run the three pipeline scripts above (`build_metadata`, `build_chunks`,
`ingest`). Nothing under `data/row` is ever modified by the pipeline —
`metadata.csv`, `data/processed`, and `data/chroma` are all derived and
safe to delete/rebuild at any time.

## Notes on this environment

- Embeddings use ONNX Runtime (`all-MiniLM-L6-v2`) instead of
  sentence-transformers/PyTorch, because PyTorch's official wheels require
  AVX2, which some older CPUs lack. Same model, portable runtime.
- `chroma-hnswlib` is pinned to `0.7.3` in `backend/requirements.txt`
  because `0.7.6` (chromadb 0.5.23's default) segfaults on non-AVX2 CPUs
  once its index grows past the first insert batch.

## Deployment

See `docker-compose.yml` for a two-container (backend + frontend) setup.
`GET /health` and `GET /version` are available for platform health checks
(Railway, Render, etc.). Configuration is entirely environment-variable
driven — see `.env.example`.
