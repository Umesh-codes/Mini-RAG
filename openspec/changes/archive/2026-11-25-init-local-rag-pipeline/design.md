# Design

## Context
The goal is to implement an offline, private RAG system using local tools. The architecture is constrained by `GUARDRAILS.md`:
- Python 3.10+ execution environment.
- LangChain ecosystem (`langchain`, `langchain-openai`, `langchain-chroma`, `langchain-text-splitters`).
- Vector storage persisted strictly to `./chroma_db`.
- Local AI server provided by LM Studio at `http://localhost:1234/v1` using dummy credentials (`api_key="lm-studio"`).
- Embedding model: `nomic-embed-text-v1.5`.
- Chat LLM: Local instruction-tuned model (e.g. Mistral / Llama).
- No cloud dependencies or complex web UIs.

See `proposal.md` for overall motivation and `specs/rag-pipeline/spec.md` for behavior contracts.

## Goals / Non-Goals

**Goals:**
- Provide a clear, clean 2-stage workflow: ingestion via `ingest.py` and interactive querying via `query.py`.
- Chunk markdown documents predictably using `RecursiveCharacterTextSplitter` (chunk size: 500, chunk overlap: 50).
- Ensure identical embedding generation in both ingestion and query stages using `OpenAIEmbeddings` configured with LM Studio's endpoint.
- Persist vectors and metadata in `./chroma_db` using `Chroma` from `langchain-chroma`.
- Restrict query generation strictly to retrieved context (top 3 chunks) to eliminate hallucinations.

**Non-Goals:**
- Web interfaces, REST APIs, or graphical front-ends (Gradio/Streamlit).
- Distributed or client-server vector databases (e.g. Pinecone, Weaviate, Milvus).
- Complex autonomous agent loops or multi-turn conversational memory.
- Multi-document format parsers beyond plain Markdown/text.

## Decisions

### 1. Client Abstraction: `langchain-openai` over Custom HTTP or Specialized Providers
- **Decision**: Use `OpenAIEmbeddings` and `ChatOpenAI` from `langchain-openai` configured with `base_url="http://localhost:1234/v1"` and `api_key="lm-studio"`.
- **Rationale**: LM Studio implements standard OpenAI-compatible endpoints (`/v1/embeddings` and `/v1/chat/completions`). Utilizing standard LangChain OpenAI classes maintains maximum compatibility, clean pipeline chaining, and avoids manual HTTP request handling.
- **Alternatives Considered**: Direct `urllib`/`requests` wrappers (would require manual vector formatting and prompt serialization); `langchain-community` LLM wrappers (less actively updated than `langchain-openai`).

### 2. Vector Persistence: `langchain-chroma` with Local Directory
- **Decision**: Store vectors in `./chroma_db` using `Chroma(persist_directory="./chroma_db", embedding_function=...)`.
- **Rationale**: Chroma operates entirely in-process without requiring a separate background service or Docker container, perfectly fitting the local offline requirement.
- **Alternatives Considered**: FAISS (requires separate pickle serialization for document text/metadata); in-memory stores (loss of persistence between CLI invocations).

### 3. Chunking Parameters
- **Decision**: Use `RecursiveCharacterTextSplitter` with `chunk_size=500` and `chunk_overlap=50`.
- **Rationale**: Provides granular chunks that preserve paragraph and header boundaries in Markdown, matching the user's specification and fitting comfortably within context limits for embedding and retrieval.
- **Alternatives Considered**: Token-based splitters (adds extra tokenizer dependency); sentence-only splitters (risk oversized chunks with long prose).

### 4. Grounded Prompt Engineering for Hallucination Prevention
- **Decision**: Use a strict system prompt and structured template:
  ```text
  You are an assistant answering questions strictly based on the provided context.
  If the context does not contain enough information to answer the question, state:
  "I do not have sufficient information in the provided context to answer this question."
  Do not use any external knowledge.

  Context:
  {context}

  Question:
  {question}
  ```
- **Rationale**: Local 7B/8B parameter models require explicit, bounded negative constraints to prevent external knowledge leakage.
- **Alternatives Considered**: Open-ended QA prompting (fails strict grounding requirements).

## Risks / Trade-offs

- **[Risk] LM Studio is offline or models are not loaded**
  → *Mitigation*: Wrap API connection in `ingest.py` and `query.py` with descriptive exception handling alerting the user to ensure LM Studio is running at `http://localhost:1234/v1` with the required models.
- **[Risk] Embedding model inconsistency across ingestion and query**
  → *Mitigation*: Define `EMBEDDING_MODEL_NAME = "nomic-embed-text-v1.5"` as a common constant or standard configuration in both scripts.
- **[Risk] Duplicate vectors added on repeated ingestion**
  → *Mitigation*: In `ingest.py`, use an identifiable collection name or clear previous entries prior to persisting new embeddings to maintain idempotent behavior.
- **[Risk] Vector database tracked by git**
  → *Mitigation*: Ensure `.gitignore` explicitly includes `chroma_db/` and `.venv/`.
