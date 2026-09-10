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

### Build the multilingual Gemini index on Windows

After the backend setup is complete and `GEMINI_API_KEY` is present in the
project's `.env` file, double-click `build_gemini_index_windows.bat` in the
project folder. It builds the V2 multilingual index using the Gemini free tier
and waits between batches to respect its rate limits.

Keep the terminal window open until it reports completion. Progress is saved
after every batch: if the process stops, run the same file again and it resumes
without embedding completed chunks again. The API key is read from `.env` and
is never copied into the script or printed to the terminal.

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
- `chroma-hnswlib` `0.7.6` (chromadb 0.5.23's pinned version) segfaults on
  non-AVX2 CPUs once its index grows past the first insert batch. Because
  chromadb hard-pins `==0.7.6`, this cannot be expressed in
  `requirements.txt` — pip would refuse to resolve it. On such a machine,
  downgrade after installing instead:

  ```bash
  pip install --no-deps chroma-hnswlib==0.7.3
  ```

  Cloud hosts (Render, etc.) run on AVX2-capable CPUs and need no override.

## Cloning this repo

`data/row` (460MB of source PDFs) is **not** tracked, so the pipeline scripts
cannot be re-run from a fresh clone. You do not need them: the vector index
ships prebuilt as `data/chroma_index.tar.gz`, and `data/processed/chunks.jsonl`
plus `data/metadata.csv` are tracked so the index can be rebuilt without the
PDFs. After cloning:

```bash
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m app.scripts.prepare_index   # expands the index, warms the model
```

`prepare_index` is idempotent — it skips the restore if an index is already
present.

## Deployment

The backend and frontend deploy as **two services from this one repo**. They
communicate over REST only, so they do not need to share a host.

### Backend → Render

`render.yaml` is a ready-to-use blueprint. Point Render at this repo and it
will pick it up. Two values must be set in the dashboard (they are marked
`sync: false` and are never committed):

- `GEMINI_API_KEY` — from [Google AI Studio](https://aistudio.google.com/apikey)
- `CORS_ORIGINS` — the Vercel origin, e.g. `["https://your-app.vercel.app"]`.
  Until this is set, the deployed UI's requests are rejected by CORS.

The build step runs `prepare_index`, which expands the committed index and
pre-downloads the ~167MB ONNX model so neither happens on the cold-start path.

### Frontend → Vercel

Import the repo with **Root Directory** set to `frontend`, and set:

- `NEXT_PUBLIC_API_BASE_URL` — the Render service URL.

This is inlined at build time, so changing it requires a redeploy, not just a
restart.

### Free-tier caveats

- Render's free tier sleeps after 15 minutes idle and takes ~1 minute to wake.
  The chat UI shows a "waking the server up" hint after 5 seconds.
- Free-tier Gemini quota is per-project and varies by model. Some keys have
  zero quota for `gemini-2.0-flash`; check with
  `GET https://generativelanguage.googleapis.com/v1beta/models` before picking
  `GEMINI_MODEL`.
- Gemini 3.x are thinking models — reasoning tokens come out of the same budget
  as the reply, so `LLM_MAX_OUTPUT_TOKENS` must be well above the default 1024
  or answers truncate mid-sentence.

### Docker

`docker-compose.yml` runs both services locally in containers.
`GET /health` and `GET /version` are available for platform health checks.
Configuration is entirely environment-variable driven — see `.env.example`.
