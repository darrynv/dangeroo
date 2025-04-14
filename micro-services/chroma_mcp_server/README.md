# Chroma MCP Server

This microservice provides semantic memory operations for RooCode via the MCP STDIO protocol, backed by ChromaDB and sentence-transformers.

## RooCode MCP Server Configuration Example

Add the following to your `.roo/mcp.json` or `mcp_settings.json`:

```json
{
  "mcpServers": {
    "chroma_manager": {
      "command": "python",
      "args": ["micro-services/chroma_mcp_server/chroma_mcp_server.py"],
      "cwd": "/path/to/project/root", // Optional: set working directory if needed
      "env": {
        "CHROMA_HOST": "chromadb", // Or "localhost" if running locally
        "CHROMA_PORT": "8000"
      },
      "disabled": false
    }
  }
}
```

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Notes

- The server will automatically advertise the tools: `chroma_upsert`, `chroma_search`, and `chroma_delete`.
- ChromaDB connection is configured via `CHROMA_HOST` and `CHROMA_PORT` environment variables.
- Code-aware chunking is performed using tree-sitter for supported languages (Python, JavaScript). Fallbacks to paragraph/sentence splitting for others.
- Embeddings are generated using the `all-MiniLM-L6-v2` model from sentence-transformers.