# Setting Up Dangeroo Mem0 with ChromaDB

This guide will help you set up the Dangeroo Mem0 MCP server with ChromaDB as the vector store and Neo4j as the graph database.

## Architecture Overview

The setup consists of three main components:

1. **FastAPI Server (dgroo-fast-api)**: Exposes the Mem0 API endpoints
2. **ChromaDB**: Vector database for semantic search
3. **Neo4j**: Graph database for entity relationships

These three components work together to provide a complete memory solution:
- ChromaDB stores text embeddings for semantic similarity search
- Neo4j stores entity relationships for structured data retrieval
- The API server orchestrates both, providing a unified interface

## Setup Instructions

### 1. Prerequisites

- Docker and Docker Compose
- Node.js (for running the MCP server)
- OpenAI API key (for embeddings and LLM)

### 2. Directory Structure

Make sure you have the following directory structure:

```
dangeroo-mem0-mcp/
├── build/
│   └── index.js
├── services/
│   ├── data/
│   │   ├── chroma/
│   │   ├── history/
│   │   └── neo4j/
│   ├── dgroo-fast-api/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── .env
│   ├── docker-compose.yml
│   └── README.md
├── mcp-example.json
└── CHROMA_SETUP.md
```

### 3. Environment Setup

1. Navigate to the services directory:
   ```
   cd dangeroo-mem0-mcp/services
   ```

2. Copy the example environment file and add your OpenAI API key:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file and replace `your_openai_api_key_here` with your actual OpenAI API key.

### 4. Starting the Services

1. Start the Docker Compose services:
   ```
   cd dangeroo-mem0-mcp/services
   docker-compose up -d
   ```

2. Verify that all services are running:
   ```
   docker-compose ps
   ```

   You should see three services running: `dgroo-fast-api`, `chroma`, and `neo4j`.

3. Test the API by visiting [http://localhost:8888/docs](http://localhost:8888/docs) in your browser.

### 5. Configuring the MCP Server

1. Update your MCP configuration to use the local API mode (already done in mcp-example.json):
   ```json
   {
     "mcpServers": {
       "mem0": {
         "command": "node",
         "args": [
           "build/index.js"
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

2. Start the MCP server (from the dangeroo-mem0-mcp directory):
   ```
   npm run start
   ```

## How It Works

### Storing Memories

When you call `add_memory` through the MCP server:

1. The MCP server forwards the request to the FastAPI server
2. The FastAPI server uses an LLM to extract facts from the memory
3. Those facts are embedded and stored in ChromaDB for semantic search
4. Entity relationships are extracted and stored in Neo4j
5. A record of the operation is saved in the SQLite history database

### Searching Memories

When you call `search_memory` through the MCP server:

1. The MCP server forwards the search to the FastAPI server
2. The FastAPI server embeds the search query
3. It searches ChromaDB for semantically similar content
4. It also queries Neo4j for related entity information
5. The results are combined and returned

## Troubleshooting

### Common Issues

1. **ChromaDB Connection Issues**
   - Check that the ChromaDB container is running: `docker-compose ps`
   - Verify the ChromaDB logs: `docker-compose logs chroma`
   - Ensure the ChromaDB_HOST and ChromaDB_PORT environment variables are set correctly

2. **Neo4j Connection Issues**
   - Check that the Neo4j container is running: `docker-compose ps`
   - Verify the Neo4j logs: `docker-compose logs neo4j`
   - Ensure the NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD environment variables are set correctly

3. **API Server Issues**
   - Check the API server logs: `docker-compose logs dgroo-fast-api`
   - Ensure the OPENAI_API_KEY is valid

### Viewing Data

- **ChromaDB**: You can use the ChromaDB API directly at http://localhost:8000/api/v1
- **Neo4j**: Browse the Neo4j database at http://localhost:7474 (username: neo4j, password: mem0graph)
- **API**: Interact with the API at http://localhost:8888/docs

## Maintenance

### Backing Up Data

To back up your data, simply archive the `data` directory:
```
tar -czf mem0_backup.tar.gz services/data
```

### Resetting Data

To completely reset your data:
1. Stop the containers: `docker-compose down`
2. Delete the data directories: `rm -rf data/chroma/* data/neo4j/* data/history/*`
3. Restart the containers: `docker-compose up -d`

## Additional Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Mem0 Documentation](https://docs.mem0.ai/)