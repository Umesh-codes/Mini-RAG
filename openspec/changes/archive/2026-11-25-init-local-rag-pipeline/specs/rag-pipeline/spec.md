# Spec Delta

## Purpose
Provides local document ingestion, vector storage, similarity search retrieval, and context-grounded question answering using an offline LM Studio instance.

## ADDED Requirements

### Requirement: Document Chunking and Persistence
The system SHALL load Markdown documents from `data/sample_notes.md`, split the content into text chunks of at most 500 characters with a 50-character overlap using RecursiveCharacterTextSplitter, compute vector embeddings using `nomic-embed-text-v1.5` via the local OpenAI-compatible endpoint at `http://localhost:1234/v1`, and persist the resulting vectors and documents to `./chroma_db`.

#### Scenario: Ingestion of sample notes
- **WHEN** the user executes `python ingest.py` against `data/sample_notes.md`
- **THEN** the system creates or updates the persistent Chroma vector collection in `./chroma_db` with chunked embeddings and prints a success summary

#### Scenario: Missing source document handling
- **WHEN** the user executes `python ingest.py` and `data/sample_notes.md` does not exist
- **THEN** the system logs a descriptive file-not-found error message and exits without corrupting `./chroma_db`

### Requirement: Semantic Chunk Retrieval
The system SHALL accept a natural language query from the CLI, generate its query embedding using `nomic-embed-text-v1.5` via `http://localhost:1234/v1`, and retrieve the top 3 most relevant context chunks from the persistent store at `./chroma_db`.

#### Scenario: Successful chunk retrieval
- **WHEN** the user submits a question through the CLI prompt in `query.py`
- **THEN** the system queries `./chroma_db` and retrieves the top 3 matching text chunks based on vector similarity

#### Scenario: Empty or uninitialized vector database
- **WHEN** the user runs `query.py` while `./chroma_db` does not exist or contains no records
- **THEN** the system warns the user that the vector database is empty and exits prompting them to run `ingest.py` first

### Requirement: Grounded Context Answer Generation
The system SHALL format a retrieval-augmented prompt containing the retrieved context chunks and the user's question, dispatch the prompt to the local LLM endpoint at `http://localhost:1234/v1`, and display an answer derived strictly and exclusively from the provided context.

#### Scenario: Answering a question supported by context
- **WHEN** the user asks a question whose facts are present in the retrieved context
- **THEN** the local LLM generates an answer grounded strictly in the retrieved text chunks

#### Scenario: Refusal when context is insufficient
- **WHEN** the user asks a question whose facts are absent from the retrieved chunks
- **THEN** the local LLM explicitly states that the retrieved documents do not contain enough information to answer the question

### Requirement: Storage and Repository Isolation
The system SHALL store all vector database files exclusively in `./chroma_db/` and configure repository ignore rules to exclude `.venv/` and `chroma_db/` from version control.

#### Scenario: Ignoring artifacts in git
- **WHEN** git status is inspected after virtual environment creation and ingestion execution
- **THEN** neither `.venv/` nor `chroma_db/` appear as untracked repository files
