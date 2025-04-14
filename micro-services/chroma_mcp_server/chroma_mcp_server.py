import os
import sys
import json
import threading
import traceback
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer
from tqdm import tqdm

from tree_sitter import Language, Parser
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_go as tsgo

# --- Configuration ---
CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
CHROMA_COLLECTION = "roo_memory_bank"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_TOKEN_LIMIT = 512  # Target tokens per chunk

# --- Load Embedding Model and Tokenizer ---
embedder = SentenceTransformer(EMBED_MODEL)
tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)

# --- Tree-sitter Setup (Python, JS, Go) ---
PY_LANGUAGE = Language(tspython.language())
JS_LANGUAGE = Language(tsjavascript.language())
GO_LANGUAGE = Language(tsgo.language())
PARSERS = {
    "py": PY_LANGUAGE,
    "js": JS_LANGUAGE,
    "go": GO_LANGUAGE,
}

def get_language_parser(file_path: str) -> Optional[Parser]:
    ext = file_path.split(".")[-1]
    lang = PARSERS.get(ext)
    if not lang:
        return None
    parser = Parser()
    parser.set_language(lang)
    return parser

# --- ChromaDB Client ---
def get_chroma_client():
    return chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        settings=Settings(allow_reset=True)
    )

def get_or_create_collection(client):
    try:
        return client.get_collection(CHROMA_COLLECTION)
    except Exception:
        return client.create_collection(CHROMA_COLLECTION)

# --- Chunking Utilities ---
def code_aware_chunking(file_path: str, content: str) -> List[Dict[str, Any]]:
    """
    Attempts to chunk code by semantic units (functions/classes) using tree-sitter.
    Falls back to paragraph/sentence splitting if parsing fails.
    """
    parser = get_language_parser(file_path)
    if parser:
        try:
            tree = parser.parse(bytes(content, "utf8"))
            root = tree.root_node
            # For Python: chunk by class/function definitions
            # For JS: chunk by function/class declarations
            # This is a simplified example; for production, expand for more languages
            chunks = []
            def extract_chunks(node, parent_name=None):
                if node.type in ("function_definition", "class_definition", "function_declaration", "method_definition"):
                    start, end = node.start_byte, node.end_byte
                    text = content[start:end]
                    tokens = tokenizer.tokenize(text)
                    if len(tokens) <= CHUNK_TOKEN_LIMIT:
                        chunks.append({
                            "text": text,
                            "start_line": node.start_point[0] + 1,
                            "end_line": node.end_point[0] + 1,
                            "parent": parent_name,
                        })
                    else:
                        # Recursively split large blocks
                        for child in node.children:
                            extract_chunks(child, parent_name=node.type)
                else:
                    for child in node.children:
                        extract_chunks(child, parent_name)
            extract_chunks(root)
            if chunks:
                return chunks
        except Exception:
            pass  # Fallback to text chunking below

    # Fallback: split by paragraphs, then sentences, then by token limit
    import re
    paragraphs = re.split(r"\n\s*\n", content)
    chunks = []
    for para in paragraphs:
        sentences = re.split(r"(?<=[.!?])\s+", para)
        current = ""
        for sent in sentences:
            if not sent.strip():
                continue
            candidate = (current + " " + sent).strip() if current else sent
            tokens = tokenizer.tokenize(candidate)
            if len(tokens) > CHUNK_TOKEN_LIMIT:
                if current:
                    chunks.append({"text": current})
                current = sent
            else:
                current = candidate
        if current:
            chunks.append({"text": current})
    return chunks

# --- Embedding Utility ---
def embed_texts(texts: List[str]) -> List[List[float]]:
    return embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True).tolist()

# --- MCP Protocol Utilities ---
def send_message(obj: dict):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()

def read_message() -> Optional[dict]:
    line = sys.stdin.readline()
    if not line:
        return None
    try:
        return json.loads(line)
    except Exception:
        return None

def mcp_error_response(id, code, message, data=None):
    resp = {
        "jsonrpc": "2.0",
        "id": id,
        "error": {
            "code": code,
            "message": message,
        }
    }
    if data:
        resp["error"]["data"] = data
    return resp

def mcp_result_response(id, result):
    return {
        "jsonrpc": "2.0",
        "id": id,
        "result": result
    }

# --- Tool Handlers ---
def handle_chroma_upsert(id, params):
    file_path = params.get("file_path")
    content = params.get("content")
    if not file_path or not content:
        send_message(mcp_error_response(id, -32602, "Missing file_path or content"))
        return
    try:
        # Chunking
        chunks = code_aware_chunking(file_path, content)
        if not chunks:
            send_message(mcp_error_response(id, -32001, "No chunks generated"))
            return
        texts = [c["text"] for c in chunks]
        embeddings = embed_texts(texts)
        ids = [f"{file_path}::chunk_{i}" for i in range(len(chunks))]
        metadatas = []
        for i, c in enumerate(chunks):
            meta = {
                "source_file": file_path,
                "chunk_index": i,
            }
            if "start_line" in c and "end_line" in c:
                meta["start_line"] = c["start_line"]
                meta["end_line"] = c["end_line"]
            if "parent" in c:
                meta["parent"] = c["parent"]
            metadatas.append(meta)
        # ChromaDB
        client = get_chroma_client()
        collection = get_or_create_collection(client)
        # Delete existing vectors for this file
        collection.delete(where={"source_file": file_path})
        # Upsert new vectors
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        send_message(mcp_result_response(id, {"status": "success", "message": f"Vectors upserted for {file_path}"}))
    except Exception as e:
        send_message(mcp_error_response(id, -32000, f"Upsert failed: {str(e)}", data=traceback.format_exc()))

def handle_chroma_search(id, params):
    query_text = params.get("query_text")
    k = params.get("k", 5)
    if not query_text:
        send_message(mcp_error_response(id, -32602, "Missing query_text"))
        return
    try:
        query_emb = embed_texts([query_text])[0]
        client = get_chroma_client()
        collection = get_or_create_collection(client)
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "source": results["metadatas"][0][i].get("source_file"),
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        send_message(mcp_result_response(id, {"status": "success", "results": formatted}))
    except Exception as e:
        send_message(mcp_error_response(id, -32000, f"Search failed: {str(e)}", data=traceback.format_exc()))

def handle_chroma_delete(id, params):
    file_path = params.get("file_path")
    if not file_path:
        send_message(mcp_error_response(id, -32602, "Missing file_path"))
        return
    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client)
        collection.delete(where={"source_file": file_path})
        send_message(mcp_result_response(id, {"status": "success", "message": f"Vectors deleted for {file_path}"}))
    except Exception as e:
        send_message(mcp_error_response(id, -32000, f"Delete failed: {str(e)}", data=traceback.format_exc()))

# --- Tool Advertisement ---
def advertise_tools():
    tools = [
        {
            "name": "chroma_upsert",
            "description": "Chunk, embed, and upsert file content into ChromaDB.",
            "params": {
                "file_path": "string",
                "content": "string"
            }
        },
        {
            "name": "chroma_search",
            "description": "Semantic search in ChromaDB.",
            "params": {
                "query_text": "string",
                "k": "integer"
            }
        },
        {
            "name": "chroma_delete",
            "description": "Delete all vectors for a file from ChromaDB.",
            "params": {
                "file_path": "string"
            }
        }
    ]
    send_message({
        "jsonrpc": "2.0",
        "method": "advertiseTools",
        "params": {"tools": tools}
    })

# --- Main MCP Loop ---
def main():
    advertise_tools()
    while True:
        req = read_message()
        if req is None:
            break
        if "method" not in req or "id" not in req:
            continue
        method = req["method"]
        id = req["id"]
        params = req.get("params", {})
        if method == "callTool":
            tool = params.get("tool")
            tool_params = params.get("params", {})
            if tool == "chroma_upsert":
                handle_chroma_upsert(id, tool_params)
            elif tool == "chroma_search":
                handle_chroma_search(id, tool_params)
            elif tool == "chroma_delete":
                handle_chroma_delete(id, tool_params)
            else:
                send_message(mcp_error_response(id, -32601, f"Unknown tool: {tool}"))
        else:
            send_message(mcp_error_response(id, -32601, f"Unknown method: {method}"))

if __name__ == "__main__":
    main()