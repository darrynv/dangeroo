# Dangeroo Mem0 Services

A collection of services to provide memory capabilities for Dangeroo using the Mem0 architecture:

## Components

1. **dgroo-fast-api** - FastAPI server that exposes the Mem0 memory API
2. **ChromaDB** - Vector database for semantic search
3. **Neo4j** - Graph database for entity relationships

## Setup

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Getting Started

1. Copy the example environment file:
   ```
   cp .env.example .env
   ```

2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Create the necessary directories:
   ```
   mkdir -p data/history data/chroma data/neo4j
   ```

4. Start the services:
   ```
   docker-compose up -d
   ```

5. Visit the FastAPI documentation at http://localhost:8888/docs

## API Endpoints

- **POST /memories** - Add new memories
- **GET /memories** - List all memories
- **GET /memories/{memory_id}** - Get a specific memory
- **POST /search** - Search memories
- **PUT /memories/{memory_id}** - Update a memory
- **DELETE /memories/{memory_id}** - Delete a memory
- **GET /memories/{memory_id}/history** - Get memory history
- **DELETE /memories** - Delete all memories
- **POST /reset** - Reset all memories

## Integration with MCP Server

Update your MCP server configuration to use the local API mode:

```json
{
  "mcpServers": {
    "mem0": {
      "command": "node",
      "args": [
        "/path/to/dangeroo-mem0-mcp/build/index.js"
      ],
      "env": {
        "MEM0_MODE": "local",
        "MEM0_API_ENDPOINT": "http://localhost:8888",
        "DEFAULT_USER_ID": "user123"
      },
      "disabled": false,
      "alwaysAllow": [
        "add_memory",
        "search_memory",
        "delete_memory"
      ]
    }
  }
}
```