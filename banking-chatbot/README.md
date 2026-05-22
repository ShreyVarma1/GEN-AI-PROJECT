# 🏦 BankBot — AI Banking Support Chatbot

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.4-blue?logo=typescript)
![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-orange?logo=google)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

A production-grade AI banking support chatbot powered by Retrieval-Augmented Generation (RAG). Upload your banking documents and get accurate, grounded answers about loans, credit cards, and banking policies — with full source attribution and streaming responses.

---

## Architecture

```
User → React Frontend (Vite + Tailwind)
              │
              ▼ REST / SSE
       FastAPI Backend
              │
    ┌─────────┴──────────┐
    │                    │
[Document Upload]   [Chat Query]
    │                    │
  Parser             Embed Query (HyDE)
  Chunker               │
  Embeddings        ChromaDB Search
  ChromaDB              │
                    Rerank (distance sort)
                        │
                    Prompt Builder
                    (context + history)
                        │
                    Google Gemini API
                        │
                    Response + Sources
                    (streaming SSE)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11) |
| LLM | Google Gemini (`gemini-2.0-flash` default, configurable) |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) — local, free |
| Vector DB | ChromaDB (persistent local) |
| Reranking | Distance-based sorting (cross-encoder optional) |
| Document Parsing | PyMuPDF (PDF), python-docx (DOCX), built-in (TXT) |
| Text Chunking | LangChain RecursiveCharacterTextSplitter |
| Session Memory | In-memory dict with rolling summarization |
| Caching | Redis (optional) |
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS |
| HTTP Client | Axios + native fetch (SSE streaming) |
| Deployment | Render.com (free tier) |
| CI/CD | GitHub Actions |
| Containers | Docker + Docker Compose |

---

## Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **Google API key** — get one free at [aistudio.google.com](https://aistudio.google.com)
- **Docker + Docker Compose** (optional, for containerized setup)

---

## Local Setup

### Option 1: Docker Compose (Recommended)

```bash
# 1. Navigate to the project
cd banking-chatbot

# 2. Set your API key in backend/.env
# Open backend/.env and set: GOOGLE_API_KEY=your_key_here

# 3. Build and start everything
docker-compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

**Backend:**
```bash
cd banking-chatbot/backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit .env and set GOOGLE_API_KEY=your_key_here

# (Optional) Generate sample documents
cd ..
python data_generator/generate_banking_docs.py
cd backend

# Start the server
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd banking-chatbot/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Opens at http://localhost:5173 (or 3000)
```

> **Note:** The backend auto-seeds sample documents from `backend/data/sample_docs/` on first startup if the vector store is empty. No manual seeding step required.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | *(required)* | Your Google AI Studio API key |
| `LLM_MODEL` | `gemini-2.0-flash` | Gemini model to use |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | sentence-transformers model |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | ChromaDB storage path |
| `CHROMA_COLLECTION_NAME` | `banking_docs` | ChromaDB collection name |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Chunks retrieved per query |
| `MAX_HISTORY_TURNS` | `10` | Conversation turns to keep |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS allowed origins (comma-separated) |
| `REDIS_URL` | *(empty)* | Redis URL for caching (optional) |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Backend API base URL |

---

## API Documentation

Full interactive docs available at `http://localhost:8000/docs` (Swagger UI).

### POST /api/v1/chat

Send a message to the chatbot.

**Request:**
```json
{
  "session_id": "optional-uuid",
  "message": "What is the interest rate on a personal loan?",
  "stream": false
}
```

**Response (stream: false):**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "answer": "Personal loan interest rates range from 10.5% to 24% p.a. depending on your credit score...",
  "sources": [
    {
      "filename": "personal_loans_faq.txt",
      "chunk_preview": "Interest rates range from 10.5% to 24% per annum...",
      "distance": 0.12
    }
  ],
  "tokens_used": 312
}
```

**Response (stream: true):** Returns `text/event-stream` with SSE events:
```
data: {"type": "sources", "sources": [...]}
data: {"type": "delta", "text": "Personal loan"}
data: {"type": "delta", "text": " interest rates..."}
data: {"type": "done"}
data: {"type": "error", "message": "..."}   ← on failure
```

### POST /api/v1/upload

Upload and index a document.

**Request:** `multipart/form-data` with `file` field (PDF, TXT, or DOCX, max 10MB)

**Response:**
```json
{
  "filename": "personal_loans_faq.txt",
  "chunks_indexed": 24,
  "status": "success",
  "message": "Successfully indexed 24 chunks from 'personal_loans_faq.txt'"
}
```

### GET /api/v1/health

Check system status.

**Response:**
```json
{
  "status": "ok",
  "vector_db": "connected",
  "documents_indexed": 5,
  "sources": ["personal_loans_faq.txt", "credit_card_policy.txt"],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### DELETE /api/v1/chat/{session_id}

Clear a chat session's history.

---

## Project Structure

```
banking-chatbot/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, startup, middleware, auto-seeding
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── dependencies.py      # Shared DI
│   │   ├── routers/
│   │   │   ├── chat.py          # POST /chat, DELETE /chat/{id}
│   │   │   ├── upload.py        # POST /upload
│   │   │   └── health.py        # GET /health
│   │   ├── services/
│   │   │   ├── rag_pipeline.py  # Full RAG orchestration (ingest + query + stream)
│   │   │   ├── llm_client.py    # Google Gemini wrapper (sync + async streaming)
│   │   │   ├── embeddings.py    # sentence-transformers singleton
│   │   │   ├── vector_store.py  # ChromaDB CRUD + similarity search
│   │   │   ├── chunker.py       # LangChain text splitter
│   │   │   └── document_parser.py # PDF/TXT/DOCX parser
│   │   ├── models/
│   │   │   ├── chat.py          # ChatRequest, ChatResponse, SourceChunk
│   │   │   └── document.py      # UploadResponse
│   │   └── utils/
│   │       ├── session_manager.py # In-memory sessions + rolling summarization
│   │       └── prompt_builder.py  # System prompt + message assembly
│   ├── data/sample_docs/        # Auto-generated seed documents (5 files)
│   ├── chroma_db/               # Persisted vector data (gitignored)
│   ├── tests/
│   │   ├── test_chat.py
│   │   ├── test_rag.py
│   │   └── test_upload.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.tsx   # Main chat area
│   │   │   ├── InputBar.tsx     # Message input + send button
│   │   │   ├── MessageBubble.tsx # Individual message rendering
│   │   │   ├── Sidebar.tsx      # Session list + management
│   │   │   ├── SourceChips.tsx  # Source attribution chips
│   │   │   ├── TypingIndicator.tsx # Animated loading indicator
│   │   │   └── UploadPanel.tsx  # Drag-and-drop file upload
│   │   ├── hooks/
│   │   │   ├── useChat.ts       # Chat state, sessions, streaming, localStorage
│   │   │   └── useUpload.ts     # File upload state + progress
│   │   ├── lib/api.ts           # Axios API client + type definitions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile
│   └── package.json
├── data_generator/
│   └── generate_banking_docs.py # Synthetic banking document generator
├── .github/workflows/
│   └── ci-cd.yml                # GitHub Actions: test + build + deploy to Render
├── docker-compose.yml
├── render.yaml                  # Render.com deployment config
├── architecture.md
└── README.md
```

---

## Running Tests

```bash
cd banking-chatbot/backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## Deployment — Render.com

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New → Blueprint
3. Connect your GitHub repo
4. Render detects `render.yaml` and creates both services automatically
5. Set `GOOGLE_API_KEY` as a secret environment variable in the Render dashboard
6. Deploy

For CI/CD auto-deploy on every push to `main`, add `RENDER_DEPLOY_HOOK_URL` to your GitHub repository secrets.

---

## What's Implemented

| Feature | Status |
|---|---|
| Conversational chatbot UI | ✅ |
| Chat history (multi-session, localStorage) | ✅ |
| Typing / loading indicator | ✅ |
| Streaming responses (SSE) | ✅ |
| RAG pipeline (ingest → chunk → embed → store → retrieve → generate) | ✅ |
| ChromaDB vector store | ✅ |
| PDF / TXT / DOCX document upload | ✅ |
| Context retention within session | ✅ |
| Rolling conversation summarization | ✅ |
| HyDE query enhancement | ✅ |
| POST /chat, POST /upload, GET /health APIs | ✅ |
| Auto-seed sample documents on startup | ✅ |
| Redis caching (optional) | ✅ |
| Docker + Docker Compose | ✅ |
| CI/CD via GitHub Actions | ✅ |
| Render.com deployment config | ✅ |
| Synthetic banking data generator | ✅ |

## What You Still Need To Do

| Task | Details |
|---|---|
| **Set your Google API key** | Add `GOOGLE_API_KEY=your_key` to `backend/.env` |
| **Deploy to Render** | Push to GitHub, connect repo on render.com, set the API key secret |
| **Add `RENDER_DEPLOY_HOOK_URL`** | Add to GitHub repo secrets for auto-deploy on push |
| **Add `GOOGLE_API_KEY`** | Add to GitHub repo secrets for CI tests to pass |
| **Record demo video** | 5–10 min walkthrough of architecture, RAG flow, and deployment |
| **Add deployment URL to README** | Replace the placeholder below once deployed |

> **Deployed URL:** https://banking-chatbot-backend-zqkq.onrender.com
                    https://banking-chatbot-frontend-zm6h.onrender.com

---

## Known Limitations

- Session history is in-memory — lost on server restart
- ChromaDB is single-node — not suitable for high-concurrency production
- No authentication or rate limiting on API endpoints
- Embedding model runs on CPU — slower for large document batches
- Cross-encoder reranking is not active (falls back to cosine distance sort)
