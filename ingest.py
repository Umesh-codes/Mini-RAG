import json
import os
import sys
import urllib.request
import warnings
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Suppress benign macOS LibreSSL / urllib3 warnings
warnings.filterwarnings("ignore")

# Configuration constants
DATA_PATH = Path("data/sample_notes.md")
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "local_rag"
API_KEY = "lm-studio"


def get_endpoint_config() -> tuple[str, str]:
    """Resolve active base URL and embedding model from environment or local server candidates."""
    candidates = [
        os.getenv("LOCAL_AI_BASE_URL"),
        "http://127.0.0.1:1235/v1",
        "http://localhost:1234/v1",
    ]
    for base_url in filter(None, candidates):
        try:
            req = urllib.request.Request(f"{base_url}/models", headers={"Authorization": f"Bearer {API_KEY}"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("id", "") for m in data.get("data", [])]
                embed_model = next((m for m in models if "nomic" in m.lower()), "nomic-embed-text-v1.5")
                return base_url, embed_model
        except Exception:
            continue
    return "http://localhost:1234/v1", "nomic-embed-text-v1.5"


def load_document(file_path: Path) -> Document:
    """Load text content from the specified file path."""
    if not file_path.exists():
        print(f"Error: Target file '{file_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    try:
        content = file_path.read_text(encoding="utf-8")
        if not content.strip():
            print(f"Error: Target file '{file_path}' is empty.", file=sys.stderr)
            sys.exit(1)
        print(f"[+] Loaded '{file_path}' ({len(content)} characters).")
        return Document(page_content=content, metadata={"source": str(file_path)})
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)


def split_document(doc: Document) -> list[Document]:
    """Split document into chunks of 500 characters with 50-character overlap."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents([doc])
    print(f"[+] Document split into {len(chunks)} chunks (size=500, overlap=50).")
    return chunks


def get_embeddings(base_url: str, model_name: str) -> OpenAIEmbeddings:
    """Initialize OpenAI-compatible embeddings pointing to the local AI server."""
    return OpenAIEmbeddings(
        base_url=base_url,
        api_key=API_KEY,
        model=model_name,
        check_embedding_ctx_length=False
    )


def ingest():
    """Main ingestion pipeline: load, chunk, embed, and persist to ChromaDB."""
    print("--- Starting Local RAG Document Ingestion ---")
    base_url, embed_model = get_endpoint_config()
    print(f"[+] Discovered local AI endpoint: {base_url} (embedding model: '{embed_model}')")

    doc = load_document(DATA_PATH)
    chunks = split_document(doc)

    embeddings = get_embeddings(base_url, embed_model)

    try:
        print(f"[+] Generating embeddings and persisting to '{CHROMA_PATH}'...")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_PATH,
            collection_name=COLLECTION_NAME
        )
        total_records = vector_store._collection.count()
        print(f"[✓] Ingestion successful! ChromaDB collection '{COLLECTION_NAME}' now contains {total_records} records.")
    except Exception as e:
        print(
            f"\n[!] Failed to generate embeddings or persist vectors: {e}\n"
            f"Please verify that your local AI server is running at {base_url} "
            f"with the embedding model '{embed_model}' loaded.",
            file=sys.stderr
        )
        sys.exit(1)


if __name__ == "__main__":
    ingest()
