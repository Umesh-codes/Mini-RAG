# Tasks

## 1. Project Setup & Scaffolding

- [x] 1.1 Create `.gitignore` ignoring `.venv/`, `chroma_db/`, `__pycache__/`, and `.env*`, and verify the entries are present
- [x] 1.2 Create `requirements.txt` containing `langchain`, `langchain-openai`, `langchain-chroma`, `langchain-text-splitters`, and `chromadb`, and verify dependencies match architecture constraints
- [x] 1.3 Create `data/sample_notes.md` with structured technical notes and domain information to serve as the local test corpus, and verify file readability

## 2. Document Ingestion Pipeline (`ingest.py`)

- [x] 2.1 Implement document loading in `ingest.py` to read `data/sample_notes.md` with graceful error handling if the file is missing
- [x] 2.2 Configure `RecursiveCharacterTextSplitter` with `chunk_size=500` and `chunk_overlap=50` to split documents into discrete chunks
- [x] 2.3 Configure `OpenAIEmbeddings` using `base_url="http://localhost:1234/v1"`, `api_key="lm-studio"`, and `model="nomic-embed-text-v1.5"`
- [x] 2.4 Initialize Chroma vector store targeting `./chroma_db`, persist chunks, and verify collection persistence and record count summary output

## 3. Query & Answer Pipeline (`query.py`)

- [x] 3.1 Implement `query.py` to connect to the persistent Chroma store in `./chroma_db` using the identical `nomic-embed-text-v1.5` embeddings configuration
- [x] 3.2 Build retriever functionality to retrieve the top 3 most relevant chunks (`k=3`) for any provided user question
- [x] 3.3 Configure `ChatOpenAI` (`base_url="http://localhost:1234/v1"`, `api_key="lm-studio"`) with a strict prompt template enforcing answers based solely on retrieved context
- [x] 3.4 Wire CLI input handling to accept questions, run similarity retrieval, pass context to LLM, and print the grounded answer

## 4. End-to-End Integration & Verification

- [x] 4.1 Execute `python ingest.py` and verify `./chroma_db` directory is populated with vector embeddings
- [x] 4.2 Execute `query.py` with an in-corpus question and verify response is strictly grounded in `data/sample_notes.md`
- [x] 4.3 Execute `query.py` with an out-of-corpus question and verify model asserts insufficient context rather than hallucinating
