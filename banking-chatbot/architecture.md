# Architecture Documentation — Banking Support Chatbot

## System Overview

A production-grade Retrieval-Augmented Generation (RAG) chatbot for banking support. It combines a React frontend, a FastAPI backend, a local vector database (ChromaDB), and the Google Gemini LLM to answer customer queries grounded in uploaded banking documents.

---

## System Components

### 1. Frontend (React + TypeScript + Vite)
- Single-page application with a two-panel layout (sidebar + chat area)
- Communicates with the backend via REST API and Server-Sent Events (SSE) for streaming
- Manages session state in `localStorage` for persistence across page reloads
- Handles file uploads with drag-and-drop and progress tracking
- Multi-session support: create, rename, delete, and switch between chat sessions

### 2. Backend (FastAPI, Python 3.11)
- RESTful API with three main endpoints: `/chat`, `/upload`, `/health`
- Orchestrates the full RAG pipeline on each query
- Manages in-memory session history with rolling summarization
- Supports both standard JSON responses and SSE streaming
- Auto-seeds sample documents from `data/sample_docs/` on first startup

### 3. RAG Pipeline
- **Document Ingestion**: Parse → Chunk → Embed → Store
- **Query Processing**: Embed (HyDE) → Retrieve → Rerank → Prompt → Generate

### 4. Vector Database (ChromaDB)
- Persistent local storage using cosine similarity
- Stores document chunks with metadata (source filename, chunk index, page hint, char count)
- Upsert with deterministic MD5-based IDs to prevent duplicates on re-upload
- Supports source-level filtering and deletion

### 5. Embedding Model (sentence-transformers)
- `all-MiniLM-L6-v2` runs entirely locally — no API cost
- Loaded once at startup as a singleton
- Produces 384-dimensional dense vectors
- Pre-downloaded at Docker build time to avoid cold start delays

### 6. LLM (Google Gemini)
- Default model: `gemini-2.0-flash` — fast and free-tier friendly
- Configurable via `LLM_MODEL` environment variable (e.g. `gemini-1.5-flash`, `gemini-2.5-flash`)
- Supports both synchronous and streaming generation
- System prompt injected as a priming exchange (compatible with all Gemini SDK versions)

### 7. Session Manager
- In-memory Python dict keyed by UUID session IDs
- Rolling summarization: older turns beyond `MAX_HISTORY_TURNS` are compressed into a text summary
- Summary is re-injected at the start of the message list to preserve conversational continuity

### 8. Redis Cache (Optional)
- SHA256-based cache key from query + chunk IDs
- 1-hour TTL on cached responses
- Gracefully disabled when `REDIS_URL` is not set

---

## RAG Query Flow (Step-by-Step)

```
User sends message + session_id
         │
         ▼
1. Session Manager retrieves last N chat turns
         │
         ▼
2. Query embedding via sentence-transformers (all-MiniLM-L6-v2)
   [HyDE enhancement: augment query with recent context for better retrieval]
         │
         ▼
3. ChromaDB cosine similarity search → top K+2 candidate chunks
         │
         ▼
4. Reranking: sort by cosine distance (lower = more relevant) → top K chunks
   [Cross-encoder reranking available as future upgrade]
         │
         ▼
5. Redis cache check (SHA256 of query + chunk IDs)
   [Cache hit → return cached response, skip LLM call]
         │
         ▼
6. PromptBuilder assembles:
   - System prompt (role, rules, today's date)
   - Rolling summary of older turns (if any)
   - Recent conversation history
   - <context> block with retrieved chunks
   - Current user message
         │
         ▼
7. Google Gemini generates response
   [Streaming: yields text deltas as SSE events via thread pool]
         │
         ▼
8. Response + sources returned to client
   Session history updated + pruned
   Result cached in Redis (1 hour TTL)
```

---

## Document Ingestion Flow

```
File upload (PDF / TXT / DOCX, max 10MB)
         │
         ▼
1. File validation (type check, size check, empty check)
         │
         ▼
2. DocumentParser extracts raw text
   - PDF: PyMuPDF (page-by-page extraction)
   - TXT: UTF-8 / Latin-1 / CP1252 decoding with fallback
   - DOCX: python-docx (paragraphs + tables)
         │
         ▼
3. TextChunker splits text
   - RecursiveCharacterTextSplitter (chunk_size=500, overlap=50)
   - Metadata attached: source, chunk_index, page_hint, char_count
         │
         ▼
4. EmbeddingService generates vectors
   - Batch encoding via sentence-transformers (all-MiniLM-L6-v2)
         │
         ▼
5. VectorStoreService upserts into ChromaDB
   - Deterministic IDs: MD5(source_chunkindex)
   - Prevents duplicate chunks on re-upload
         │
         ▼
Return: {filename, chunks_indexed, status, message}
```

---

## Streaming Flow (SSE)

```
POST /chat  { stream: true }
         │
         ▼
FastAPI StreamingResponse (media_type: text/event-stream)
         │
         ▼
RAG pipeline runs retrieval synchronously
         │
         ▼
Yields: data: {"type": "sources", "sources": [...]}
         │
         ▼
Gemini streaming via thread pool (ThreadPoolExecutor + asyncio.Queue)
         │
         ▼
Yields: data: {"type": "delta", "text": "..."}  (per chunk)
         │
         ▼
Yields: data: {"type": "done"}
         │
         ▼
Session history updated after stream completes
```

---

## Session Management

Sessions are stored in an in-memory Python dictionary keyed by UUID. Each session holds a list of `{role, content}` message dicts.

**Pruning strategy:**
- After each turn, if history exceeds `MAX_HISTORY_TURNS * 2` messages, older turns are summarized into a rolling text summary
- The summary is injected at the start of the message list as a priming exchange
- This keeps the LLM context window manageable while preserving conversational continuity

**Frontend persistence:**
- Session index and per-session messages are stored in `localStorage`
- Sessions survive page reloads; up to 50 sessions retained
- Backend session IDs are reused across reloads via the stored session UUID

**Limitation:** Backend sessions are in-memory only — lost on server restart. For production, replace with Redis or a database.

---

## Frontend Architecture

```
App.tsx
├── Sidebar.tsx          ← session list, new chat, rename, delete
├── ChatWindow.tsx        ← message list, auto-scroll
│   ├── MessageBubble.tsx ← user/assistant message rendering
│   │   └── SourceChips.tsx ← source attribution chips
│   └── TypingIndicator.tsx ← animated loading dots
├── InputBar.tsx          ← text input, send button, abort
└── UploadPanel.tsx       ← drag-and-drop file upload, progress bar

Hooks:
├── useChat.ts   ← all chat state, session management, SSE streaming, localStorage
└── useUpload.ts ← file upload state, progress tracking

API Client:
└── lib/api.ts   ← Axios client, type definitions, error normalization
```

---

## Design Decisions

### Why Google Gemini?
- Free tier available via Google AI Studio (no credit card required)
- `gemini-2.0-flash` is fast and cost-efficient for grounded Q&A
- Configurable via `LLM_MODEL` env var — swap to `gemini-2.5-flash` or `gemini-1.5-pro` for higher quality

### Why ChromaDB?
- Zero infrastructure overhead — runs as an embedded library
- Persistent local storage with no external service dependency
- Free tier compatible (no cloud costs)
- Cosine similarity is well-suited for semantic search over text embeddings

### Why sentence-transformers locally?
- Eliminates per-query embedding API costs
- `all-MiniLM-L6-v2` is fast (CPU-friendly), small (80MB), and produces high-quality embeddings for English text
- Model is pre-downloaded at Docker build time to avoid cold start delays

### Why HyDE (Hypothetical Document Embeddings)?
- Standard query embedding can miss relevant chunks when query phrasing differs from document language
- HyDE augments the query with recent conversation context to improve retrieval recall
- Implemented as context-augmented query embedding (lightweight approximation)

### Why SSE over WebSockets?
- SSE is simpler for unidirectional server-to-client streaming
- Works natively with `fetch` API — no additional library needed
- Sufficient for the chatbot use case (client sends one message, server streams one response)

---

## Scalability Considerations

| Concern | Current Approach | Production Upgrade |
|---|---|---|
| Session storage | In-memory dict | Redis or PostgreSQL |
| Vector DB | ChromaDB local | Pinecone, Weaviate, or pgvector |
| Embedding | Local CPU | GPU instance or embedding API |
| LLM | Gemini Flash | Gemini Pro or fine-tuned model |
| Caching | Redis (optional) | Redis Cluster |
| Auth | None | JWT + API keys |
| Rate limiting | None | FastAPI middleware + Redis |
| Horizontal scaling | Single instance | Stateless backend + shared vector DB |
| Reranking | Distance sort | cross-encoder/ms-marco-MiniLM-L-6-v2 |

---

## Security Notes

- API keys are loaded from environment variables only — never hardcoded
- File uploads are validated for type, size, and emptiness before processing
- CORS origins are configurable via `ALLOWED_ORIGINS` env var
- All errors return structured JSON — no raw stack traces exposed to clients
- Input validation via Pydantic models on all endpoints
- `.env` is gitignored — secrets never committed to the repository

---

## CI/CD Pipeline (GitHub Actions)

```
Push to main / Pull Request
         │
         ▼
┌────────────────────┐    ┌────────────────────┐
│  Backend Tests     │    │  Frontend Build    │
│  (pytest)          │    │  (tsc + npm build) │
└────────┬───────────┘    └────────┬───────────┘
         └──────────┬──────────────┘
                    ▼
           Deploy to Render
           (via deploy hook)
           [only on push to main]
```
