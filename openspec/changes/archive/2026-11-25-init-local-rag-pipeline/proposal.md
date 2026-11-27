# Proposal

## Why
Developers and researchers often need to query private local Markdown and text notes using Large Language Models without leaking sensitive data to external cloud providers. Setting up a minimal, offline-first Retrieval-Augmented Generation (RAG) pipeline backed by local models (via LM Studio) and an embedded vector store provides a fast, privacy-preserving, and verifiable knowledge retrieval foundation.

## What Changes
This proposal establishes the initial baseline for the local RAG pipeline:
- **Project Scaffolding**: Add `requirements.txt` pinning required packages (`langchain`, `langchain-openai`, `langchain-chroma`, `langchain-text-splitters`, `chromadb`), `.gitignore` ignoring `.venv/` and vector database files `./chroma_db/`, and a sample knowledge base file at `data/sample_notes.md`.
- **Document Ingestion (`ingest.py`)**: Script that reads `data/sample_notes.md`, chunks content with `RecursiveCharacterTextSplitter` (chunk size: 500, overlap: 50), generates embeddings via the local LM Studio endpoint (`http://localhost:1234/v1`) using `nomic-embed-text-v1.5`, and persists vector representations into `./chroma_db`.
- **CLI Query Interface (`query.py`)**: Interactive CLI script that accepts a user prompt, embeds the query using `nomic-embed-text-v1.5`, retrieves the top 3 matching chunks from `./chroma_db`, formats a grounded prompt instructing the local LLM to answer strictly from retrieved context, and outputs the generated response.

## Capabilities

### New Capabilities
- `rag-pipeline`: End-to-end local document ingestion, chunking, vector storage with ChromaDB, and context-grounded retrieval questioning via local LM Studio models.

### Modified Capabilities
*(None)*

## Impact
- **Dependencies**: Adds `langchain`, `langchain-openai`, `langchain-chroma`, `langchain-text-splitters`, and `chromadb`.
- **Files Created**: `requirements.txt`, `.gitignore`, `data/sample_notes.md`, `ingest.py`, and `query.py`.
- **Local Storage**: Creates persistent directory `./chroma_db/`.
- **Services**: Connects to local LM Studio server at `http://localhost:1234/v1`.
