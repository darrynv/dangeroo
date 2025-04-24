# Dangeroo MCP Server Technical Documentation

This document provides detailed technical information about the Dangeroo MCP Server implementation, focusing on how it integrates with the FastAPI service, ChromaDB, and Neo4j.

## MCP Server Implementation

The MCP (Model Context Protocol) Server in the Dangeroo system acts as a bridge between the Calling Process and the memory management backend. It implements tools that the Calling Process can use to store, retrieve, and manage memory.

```mermaid
classDiagram
    class Mem0MCPServer {
        -Server server
        -StorageMode storageMode
        -Memory? localClient
        -MemoryClient? cloudClient
        -LocalApiClient? localApiClient
        -boolean isReady
        +constructor()
        -initializeClient()
        -setupToolHandlers()
        -handleAddMemory()
        -handleSearchMemory()
        -handleDeleteMemory()
        +start()
    }
    
    class StorageMode {
        <<enumeration>>
        CLOUD
        LOCAL_API
        IN_MEMORY
    }
    
    class LocalApiClient {
        -string baseUrl
        +constructor(apiEndpoint)
        +add(messages, options)
        +search(query, options)
        +delete(memoryId, options)
        +getAll(options)
    }
    
    Mem0MCPServer --> StorageMode
    Mem0MCPServer --> LocalApiClient
```

## Storage Modes

The MCP Server supports three different storage modes:

```mermaid
flowchart TD
    Start[Start MCP Server] --> CheckMode{Check Storage Mode}
    
    CheckMode -->|MEM0_MODE=cloud| Cloud[Cloud Mode]
    CheckMode -->|MEM0_MODE=local| Local[Local API Mode]
    CheckMode -->|MEM0_MODE=memory| Memory[In-Memory Mode]
    CheckMode -->|default| Cloud
    
    Cloud --> InitCloud[Initialize Cloud Client<br>Requires MEM0_API_KEY]
    Local --> InitLocal[Initialize Local API Client<br>Requires MEM0_API_ENDPOINT]
    Memory --> InitMemory[Initialize In-Memory Client<br>Requires OPENAI_API_KEY]
    
    InitCloud & InitLocal & InitMemory --> Ready[MCP Server Ready]
```

## Tool Implementation Details

### add_memory Tool

```mermaid
sequenceDiagram
    participant CallingProcess as Calling Process
    participant MCP as MCP Server
    participant Client as Memory Client
    participant API as FastAPI Service
    
    CallingProcess->>MCP: add_memory(content, userId, ...)
    
    alt Cloud Mode
        MCP->>Client: cloudClient.add(messages, options)
        Client->>API: Remote API Call
    else Local API Mode
        MCP->>Client: localApiClient.add(messages, options)
        Client->>API: HTTP POST to /memories
    else In-Memory Mode
        MCP->>Client: localClient.add(messages, options)
        Client->>Client: Process in memory
    end
    
    API-->>Client: Response with memory ID
    Client-->>MCP: Result
    MCP-->>CallingProcess: Success message
```

### search_memory Tool

```mermaid
sequenceDiagram
    participant CallingProcess as Calling Process
    participant MCP as MCP Server
    participant Client as Memory Client
    participant API as FastAPI Service
    
    CallingProcess->>MCP: search_memory(query, userId, ...)
    
    alt Cloud Mode
        MCP->>Client: cloudClient.search(query, options)
        Client->>API: Remote API Call
    else Local API Mode
        MCP->>Client: localApiClient.search(query, options)
        Client->>API: HTTP POST to /search
    else In-Memory Mode
        MCP->>Client: localClient.search(query, options)
        Client->>Client: Process in memory
    end
    
    API-->>Client: Search results
    Client-->>MCP: Formatted results
    MCP-->>CallingProcess: JSON result
```

## MCP Configuration

The MCP Server is configured through the `mcp-example.json` file:

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

## FastAPI Integration

The MCP Server communicates with the FastAPI service through REST API calls in the LocalApiClient:

```mermaid
classDiagram
    class LocalApiClient {
        -string baseUrl
        +constructor(apiEndpoint)
        +add(messages, options) : Promise
        +search(query, options) : Promise
        +delete(memoryId, options) : Promise
        +getAll(options) : Promise
    }
    
    class FastAPIEndpoints {
        +POST /memories
        +POST /search
        +GET /memories
        +GET /memories/:id
        +DELETE /memories/:id
        +PUT /memories/:id
    }
    
    LocalApiClient --> FastAPIEndpoints : HTTP Requests
```

## Memory Data Flow

### Add Memory Data Flow

```mermaid
flowchart TD
    CallingProcess[Calling Process] -->|"Tool call"| MCP[MCP Server]
    MCP -->|"HTTP Request"| FastAPI[FastAPI Service]
    
    FastAPI -->|"Format message"| Memory[Memory Module]
    
    Memory -->|"Generate embeddings"| OpenAI[OpenAI API]
    OpenAI -->|"Return embeddings"| Memory
    
    Memory -->|"Extract facts"| OpenAILLM[OpenAI LLM]
    OpenAILLM -->|"Return facts"| Memory
    
    Memory -->|"Store vector"| Chroma[ChromaDB]
    Memory -->|"Store relationships"| Neo4j[Neo4j]
    Memory -->|"Log history"| SQLite[SQLite DB]
    
    Chroma & Neo4j & SQLite -->|"Success"| Memory
    Memory -->|"Success + ID"| FastAPI
    FastAPI -->|"Response"| MCP
    MCP -->|"Tool response"| CallingProcess

    classDef ai fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef api fill:#dae8fc,stroke:#6c8ebf,stroke-width:1px;
    classDef db fill:#d5e8d4,stroke:#82b366,stroke-width:1px;
    
    class CallingProcess,OpenAI,OpenAILLM ai;
    class MCP,FastAPI,Memory api;
    class Chroma,Neo4j,SQLite db;
```

### Search Memory Data Flow

```mermaid
flowchart TD
    CallingProcess[Calling Process] -->|"Tool call"| MCP[MCP Server]
    MCP -->|"HTTP Request"| FastAPI[FastAPI Service]
    
    FastAPI -->|"Format query"| Memory[Memory Module]
    
    Memory -->|"Generate query embedding"| OpenAI[OpenAI API]
    OpenAI -->|"Return embedding"| Memory
    
    Memory -->|"Semantic search"| Chroma[ChromaDB]
    Memory -->|"Entity search"| Neo4j[Neo4j]
    
    Chroma -->|"Vector matches"| Memory
    Neo4j -->|"Entity matches"| Memory
    
    Memory -->|"Combined results"| FastAPI
    FastAPI -->|"Formatted response"| MCP
    MCP -->|"Tool response"| CallingProcess

    classDef ai fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef api fill:#dae8fc,stroke:#6c8ebf,stroke-width:1px;
    classDef db fill:#d5e8d4,stroke:#82b366,stroke-width:1px;
    
    class CallingProcess,OpenAI ai;
    class MCP,FastAPI,Memory api;
    class Chroma,Neo4j db;
```

## ChromaDB Collection Structure

ChromaDB stores memory vectors in a collection called "memories":

```mermaid
erDiagram
    MEMORIES {
        string id "Unique memory ID"
        vector embedding "Text embedding vector"
        string document "Original text content"
        json metadata "Associated metadata"
    }
    
    METADATA {
        string memory_id "Memory identifier"
        string user_id "User identifier"
        string run_id "Optional session identifier"
        string agent_id "Optional agent identifier"
        json custom_metadata "Additional metadata"
        timestamp created_at "Creation timestamp"
        timestamp updated_at "Last update timestamp"
    }
    
    MEMORIES ||--|| METADATA : contains
```

## Neo4j Graph Model

Neo4j stores entity relationships extracted from memories:

```mermaid
graph TD
    Memory((Memory)) -->|CONTAINS| Entity1((Entity))
    Memory -->|CONTAINS| Entity2((Entity))
    Memory -->|CONTAINS| Entity3((Entity))
    
    Entity1 -->|RELATIONSHIP| Entity2
    Entity2 -->|RELATIONSHIP| Entity3
    Entity3 -->|RELATIONSHIP| Entity1
    
    Memory -->|BELONGS_TO| User((User))
    
    subgraph "Entity Properties"
        Entity1 -.-> EntityProps1[name<br>type<br>properties]
        Entity2 -.-> EntityProps2[name<br>type<br>properties]
        Entity3 -.-> EntityProps3[name<br>type<br>properties]
    end
    
    subgraph "Memory Properties"
        Memory -.-> MemoryProps[memory_id<br>user_id<br>run_id<br>agent_id<br>created_at]
    end
    
    classDef entity fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef memory fill:#dae8fc,stroke:#6c8ebf,stroke-width:1px;
    classDef props fill:#d5e8d4,stroke:#82b366,stroke-width:1px;
    
    class Entity1,Entity2,Entity3,User entity;
    class Memory memory;
    class EntityProps1,EntityProps2,EntityProps3,MemoryProps props;
```

## Complete System Integration

```mermaid
graph TB
    subgraph "Calling Process Environment"
        CallingProcess[Calling Process]
        MCPTools["MCP Tools<br>- add_memory<br>- search_memory<br>- delete_memory"]
    end
    
    subgraph "MCP Server"
        MCP[MCP Server]
        LocalAPI[LocalApiClient]
    end
    
    subgraph "FastAPI Service"
        FastAPI[FastAPI]
        MemoryModule[Memory Module]
        Routes["Endpoints<br>- /memories<br>- /search<br>- /memories/{id}"]
    end
    
    subgraph "Storage"
        ChromaDB[(ChromaDB)]
        Neo4jDB[(Neo4j)]
        HistoryDB[(SQLite)]
    end
    
    subgraph "External Services"
        OpenAI[OpenAI API]
    end
    
    CallingProcess -->|"Tool Calls"| MCPTools
    MCPTools -->|"Invokes"| MCP
    MCP -->|"HTTP Requests"| LocalAPI
    LocalAPI -->|"REST API"| Routes
    Routes -->|"Process"| FastAPI
    FastAPI -->|"Delegate"| MemoryModule
    
    MemoryModule -->|"Vector Operations"| ChromaDB
    MemoryModule -->|"Graph Operations"| Neo4jDB
    MemoryModule -->|"History Tracking"| HistoryDB
    MemoryModule -->|"Embeddings & LLM"| OpenAI
    
    classDef ai fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef server fill:#dae8fc,stroke:#6c8ebf,stroke-width:1px;
    classDef api fill:#d5e8d4,stroke:#82b366,stroke-width:1px;
    classDef db fill:#fff2cc,stroke:#d6b656,stroke-width:1px;
    
    class CallingProcess,OpenAI ai;
    class MCP,LocalAPI,MCPTools server;
    class FastAPI,MemoryModule,Routes api;
    class ChromaDB,Neo4jDB,HistoryDB db;
```

## Environment Configuration

The system relies on environment variables for configuration:

### MCP Server Environment Variables
- `MEM0_MODE`: Storage mode (`cloud`, `local`, or `memory`)
- `MEM0_API_KEY`: API key for cloud mode
- `MEM0_API_ENDPOINT`: API endpoint for local API mode (e.g., `http://localhost:8888`)
- `OPENAI_API_KEY`: OpenAI API key for embeddings and LLM
- `DEFAULT_USER_ID`: Default user ID for memory operations

### FastAPI Service Environment Variables
- `CHROMA_HOST`: ChromaDB host (default: `chroma`)
- `CHROMA_PORT`: ChromaDB port (default: `8000`)
- `CHROMA_COLLECTION_NAME`: ChromaDB collection name (default: `memories`)
- `CHROMA_PATH`: ChromaDB storage path (default: `/app/data/chroma`)
- `NEO4J_URI`: Neo4j URI (default: `bolt://neo4j:7687`)
- `NEO4J_USERNAME`: Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD`: Neo4j password (default: `mem0graph`)
- `OPENAI_API_KEY`: OpenAI API key
- `HISTORY_DB_PATH`: Path to history SQLite database (default: `/app/data/history/history.db`)