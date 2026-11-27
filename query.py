import json
import os
import sys
import urllib.request
import warnings
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma

# Suppress benign macOS LibreSSL / urllib3 warnings
warnings.filterwarnings("ignore")

# Configuration constants
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "local_rag"
API_KEY = "lm-studio"
TOP_K = 3

SYSTEM_PROMPT = (
    "You are a strict and truthful assistant that answers questions based solely and "
    "exclusively on the provided context. Do NOT use outside knowledge, speculate, or fabricate answers.\n"
    "If the answer cannot be found directly in the context, your response MUST be:\n"
    "\"I do not have sufficient information in the provided context to answer this question.\""
)

HUMAN_PROMPT = (
    "Context:\n"
    "---------------------\n"
    "{context}\n"
    "---------------------\n\n"
    "Question: {question}\n\n"
    "Answer:"
)


def get_endpoint_config() -> tuple[str, str, str]:
    """Resolve active base URL, embedding model, and chat model from environment or local server candidates."""
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
                chat_model = next((m for m in models if "instruct" in m.lower() or "chat" in m.lower()), models[0] if models else "local-model")
                return base_url, embed_model, chat_model
        except Exception:
            continue
    return "http://localhost:1234/v1", "nomic-embed-text-v1.5", "local-model"


def get_vector_store(base_url: str, embed_model: str) -> Chroma:
    """Initialize connection to local persistent ChromaDB store."""
    db_path = Path(CHROMA_PATH)
    if not db_path.exists() or not any(db_path.iterdir()):
        print(
            f"Error: Vector database at '{CHROMA_PATH}' is missing or uninitialized.\n"
            f"Please run 'python ingest.py' first to index your documents.",
            file=sys.stderr
        )
        sys.exit(1)

    embeddings = OpenAIEmbeddings(
        base_url=base_url,
        api_key=API_KEY,
        model=embed_model,
        check_embedding_ctx_length=False
    )
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )
    if vector_store._collection.count() == 0:
        print(
            f"Warning: Vector database at '{CHROMA_PATH}' contains no records.\n"
            f"Please run 'python ingest.py' first to populate the vector store.",
            file=sys.stderr
        )
        sys.exit(1)

    return vector_store


def format_context(documents: list) -> str:
    """Format retrieved document chunks into a single readable string."""
    formatted_chunks = []
    for i, doc in enumerate(documents, start=1):
        source = doc.metadata.get("source", "unknown")
        formatted_chunks.append(f"[Chunk {i} | Source: {source}]\n{doc.page_content.strip()}")
    return "\n\n".join(formatted_chunks)


def ask_question(question: str, vector_store: Chroma, llm: ChatOpenAI, base_url: str, embed_model: str):
    """Retrieve top-3 chunks, construct grounded prompt, and stream/print answer."""
    print(f"\n[?] Question: {question}")
    print(f"[*] Retrieving top {TOP_K} matching chunks from '{CHROMA_PATH}'...")

    try:
        results = vector_store.similarity_search(question, k=TOP_K)
    except Exception as e:
        print(
            f"\n[!] Failed to generate query embeddings or query ChromaDB: {e}\n"
            f"Ensure your local AI server is running at {base_url} with '{embed_model}' loaded.",
            file=sys.stderr
        )
        return

    if not results:
        print("[!] No matching context chunks retrieved.")
        return

    print(f"[+] Retrieved {len(results)} context chunks.")
    context_text = format_context(results)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT)
    ])

    chain = prompt_template | llm

    print("[*] Generating grounded response from local LLM...\n")
    try:
        response = chain.invoke({
            "context": context_text,
            "question": question
        })
        print("=== Answer ===")
        print(response.content.strip())
        print("==============\n")
    except Exception as e:
        print(
            f"\n[!] LLM generation failed: {e}\n"
            f"Ensure your local AI server is reachable at {base_url}.",
            file=sys.stderr
        )


def main():
    """Main CLI entrypoint."""
    base_url, embed_model, chat_model = get_endpoint_config()
    vector_store = get_vector_store(base_url, embed_model)
    llm = ChatOpenAI(
        base_url=base_url,
        api_key=API_KEY,
        model=chat_model,
        temperature=0.0
    )

    # Single-shot query argument mode
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        ask_question(query, vector_store, llm, base_url, embed_model)
        return

    # Interactive CLI loop
    print("=== Local RAG Assistant Interactive Query CLI ===")
    print(f"Connected to {base_url} (LLM: '{chat_model}')")
    print("Type your question and press Enter. Type 'exit' or 'quit' to close.")
    while True:
        try:
            query = input("\nEnter Question > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit", "q"):
                print("Exiting.")
                break
            ask_question(query, vector_store, llm, base_url, embed_model)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break


if __name__ == "__main__":
    main()
