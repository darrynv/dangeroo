# Dangeroo Mem0 MCP Server Architecture

This document provides a detailed overview of the Dangeroo Mem0 MCP Server architecture, focusing on the relationship between FastAPI, Qdrant, and Neo4j services.

## System Architecture

```mermaid
graph TB
    CallingProcess["Calling Process"]
    MCP["MCP Server (Node.js)"]
    FastAPI["FastAPI Service"]
    Qdrant["Qdrant (Vector DB)"]
    Neo4j["Neo4j (Graph DB)"]
    History["SQLite (History DB)"]
    OpenAI["OpenAI API"]
    OpenTelemetry["OpenTelemetry Collector"]
    Zipkin["Zipkin (Monitoring)"]

    CallingProcess -->|Tool calls| MCP
    MCP -->|REST API| FastAPI
    FastAPI -->|Vector Queries| Qdrant
    FastAPI -->|Graph Queries| Neo4j
    FastAPI -->|History Tracking| History
    FastAPI -->|Embeddings & LLM| OpenAI
    FastAPI -->|Telemetry| OpenTelemetry
    OpenTelemetry -->|Traces| Zipkin

    classDef aiComponent fill:#f9d5e5,stroke:#333,stroke-width:1px;
    classDef apiComponent fill:#eeeeee,stroke:#333,stroke-width:1px;
    classDef dbComponent fill:#d5e8d4,stroke:#333,stroke-width:1px;
    classDef monitoringComponent fill:#fff2cc,stroke:#333,stroke-width:1px;

    class CallingProcess aiComponent;
    class MCP,FastAPI apiComponent;
    class Qdrant,Neo4j,History dbComponent;
    class OpenTelemetry,Zipkin monitoringComponent;
    class OpenAI aiComponent;
```

## C4 Container Diagram

```mermaid
C4Container
    title Container diagram for Dangeroo Mem0 MCP Server

    Person(user, "User", "A user interacting with Calling Process")
    
    System_Boundary(dangeroo, "Dangeroo Mem0 MCP System") {
        Container(callingProcess, "Calling Process", "AI Assistant", "Provides AI capabilities and memory tools")
        
        Container_Boundary(mcpServer, "MCP Server") {
            Container(mcp, "MCP Server", "Node.js", "Routes Calling Process tool calls to appropriate endpoints")
        }
        
        Container_Boundary(backend, "FastAPI Backend") {
            Container(fastApi, "FastAPI Service", "Python", "Provides memory API endpoints")
            ContainerDb(qdrant, "Qdrant", "Vector Database", "Stores vector embeddings for semantic search")
            ContainerDb(neo4j, "Neo4j", "Graph Database", "Stores entity relationships")
            ContainerDb(sqlite, "SQLite", "History Database", "Tracks memory changes")
        }
        
        System_Ext(openai, "OpenAI API", "Provides embeddings and LLM capabilities")
        
        Container_Boundary(monitoring, "Monitoring") {
            Container(telemetry, "OpenTelemetry", "Collector", "Collects system metrics and traces")
            Container(zipkin, "Zipkin", "Monitoring UI", "Visualizes system traces")
        }
    }
    
    Rel(user, callingProcess, "Interacts with")
    Rel(callingProcess, mcp, "Makes tool calls")
    Rel(mcp, fastApi, "REST API calls")
    Rel(fastApi, qdrant, "Vector queries")
    Rel(fastApi, neo4j, "Graph queries")
    Rel(fastApi, sqlite, "Tracks history")
    Rel(fastApi, openai, "Embedding generation and LLM calls")
    Rel(fastApi, telemetry, "Reports metrics")
    Rel(telemetry, zipkin, "Forwards traces")
```

## Detailed Component View
```mermaid
graph TD
    subgraph Calling_Process
        CallingProcess["Calling Process"]
    end

    subgraph MCP_Server_NodeJS
        MCP["MCP Server"]
        AddTool["add_memory Tool"]
        SearchTool["search_memory Tool"]
        DeleteTool["delete_memory Tool"]
    end

    subgraph FastAPI_Service
        API["FastAPI Endpoints"]
        MemoryModule["Memory Module"]
        VectorStore["Vector Store Client"]
        GraphStore["Graph Store Client"]
        EmbeddingClient["Embedding Client"]
        LLMClient["LLM Client"]
    end

    subgraph Databases
        QdrantDB["Qdrant\n(memories collection)"]
        Neo4jDB["Neo4j\n(entities & relationships)"]
        HistoryDB["SQLite\n(history.db)"]
    end

    subgraph External_Services
        OpenAIAPI["OpenAI API"]
    end

    subgraph Monitoring
        OTEL["OpenTelemetry"]
        ZipkinUI["Zipkin UI"]
    end

    CallingProcess -->|Tool calls| MCP
    MCP -->|Invokes| AddTool & SearchTool & DeleteTool
    
    AddTool -->|POST /memories| API
    SearchTool -->|POST /search| API
    DeleteTool -->|DELETE /memories/id| API
    
    API -->|Uses| MemoryModule
    MemoryModule -->|Vector operations| VectorStore
    MemoryModule -->|Graph operations| GraphStore
    MemoryModule -->|Embedding generation| EmbeddingClient
    MemoryModule -->|Fact extraction| LLMClient
    
    VectorStore -->|Stores points| QdrantDB
    GraphStore -->|Stores relationships| Neo4jDB
    MemoryModule -->|Logs changes| HistoryDB
    
    EmbeddingClient -->|text-embedding-3-small| OpenAIAPI
    LLMClient -->|gpt-4o| OpenAIAPI
    
    API -->|Sends traces| OTEL
    OTEL -->|Visualizes| ZipkinUI
```

## Memory Storage Flow - add_memory

```mermaid
sequenceDiagram
    participant CallingProcess as Calling Process
    participant MCP as MCP Server
    participant API as FastAPI Service
    participant Mem0 as Memory Module
    participant OpenAI as OpenAI API
    participant Qdrant as Qdrant
    participant Neo4j as Neo4j
    participant History as History DB

    CallingProcess->>MCP: add_memory tool call
    MCP->>API: POST /memories
    API->>Mem0: Memory.add()
    
    Mem0->>OpenAI: Generate embeddings (text-embedding-3-small)
    OpenAI-->>Mem0: Return embeddings
    
    Mem0->>OpenAI: Extract facts (gpt-4o)
    OpenAI-->>Mem0: Return extracted facts
    
    par Store data in databases
        Mem0->>Qdrant: Store vector points
        Qdrant-->>Mem0: Confirm storage
        
        Mem0->>Neo4j: Store entity relationships
        Neo4j-->>Mem0: Confirm storage
        
        Mem0->>History: Log memory creation
        History-->>Mem0: Confirm log
    end
    
    Mem0-->>API: Return memory ID
    API-->>MCP: Return success response
    MCP-->>CallingProcess: Return success message
```

## Memory Retrieval Flow - search_memory

```mermaid
sequenceDiagram
    participant CallingProcess as Calling Process
    participant MCP as MCP Server
    participant API as FastAPI Service
    participant Mem0 as Memory Module
    participant OpenAI as OpenAI API
    participant Qdrant as Qdrant
    participant Neo4j as Neo4j

    CallingProcess->>MCP: search_memory tool call
    MCP->>API: POST /search
    API->>Mem0: Memory.search()
    
    Mem0->>OpenAI: Generate query embeddings
    OpenAI-->>Mem0: Return embeddings
    
    par Query databases
        Mem0->>Qdrant: Semantic search
        Qdrant-->>Mem0: Return relevant points
        
        Mem0->>Neo4j: Query related entities
        Neo4j-->>Mem0: Return graph relationships
    end
    
    Mem0->>Mem0: Combine and rank results
    
    Mem0-->>API: Return search results
    API-->>MCP: Return formatted results
    MCP-->>CallingProcess: Return memory content
```

## Data Model

### Qdrant Collection Schema

```mermaid
classDiagram
    class QdrantPoint {
        +String/Int id
        +Vector vector
        +Map payload
    }

    class Payload {
        +String memory_id
        +String user_id
        +String? run_id
        +String? agent_id
        +String document
        +Map? custom_metadata
        +Timestamp created_at
        +Timestamp updated_at
    }

    QdrantPoint --> Payload : contains
```

### Neo4j Graph Schema

```mermaid
classDiagram
    class Entity {
        +String entity_id
        +String name
        +String type
        +Map properties
    }

    class Relationship {
        +String relationship_id
        +String type
        +Map properties
    }

    class Memory {
        +String memory_id
        +String user_id
        +String? run_id
        +String? agent_id
        +Timestamp created_at
    }

    Entity "1" -- "many" Relationship : SOURCE_OF
    Entity "1" -- "many" Relationship : TARGET_OF
    Memory "1" -- "many" Entity : CONTAINS
```

## API Flow for add_memory and search_memory

### add_memory API Flow

```mermaid
flowchart TD
    A[Start] --> B[Calling Process calls add_memory tool]
    B --> C{MCP Server}
    C --> |POST /memories| D[FastAPI endpoint]
    D --> E[Validate input]
    E --> F[Format messages & options]
    F --> G[Memory.add method]
    
    G --> H[Generate Embeddings]
    H --> I[Extract Facts]
    
    I --> J{Process Storage}
    J --> |Vector Store| K[Store in Qdrant]
    J --> |Graph Store| L[Store in Neo4j]
    J --> |History| M[Log in SQLite]
    
    K & L & M --> N[Return memory ID]
    N --> O[Return success to MCP]
    O --> P[Return to Calling Process]
    P --> Q[End]
```

### search_memory API Flow

```mermaid
flowchart TD
    A[Start] --> B[Calling Process calls search_memory tool]
    B --> C{MCP Server}
    C --> |POST /search| D[FastAPI endpoint]
    D --> E[Validate query]
    E --> F[Format query & options]
    F --> G[Memory.search method]
    
    G --> H[Generate Query Embeddings]
    
    H --> I{Parallel Query}
    I --> |Vector Search| J[Query Qdrant]
    I --> |Graph Query| K[Query Neo4j]
    
    J & K --> L[Combine & Rank Results]
    L --> M[Format response]
    M --> N[Return to MCP]
    N --> O[Return to Calling Process]
    O --> P[End]
```

## Docker Containers and Network Architecture

```mermaid
graph TB
    subgraph "Docker Network: dangeroo_network"
        FastAPI["dgroo-fast-api<br>Port: 8888:8000"]
        Qdrant["qdrant<br>Ports: 6333:6333, 6334:6334"]
        Neo4j["neo4j<br>Ports: 7474:7474, 7687:7687"]
        OTEL["otel-collector<br>Ports: 4317, 4318, 13133"]
        Zipkin["zipkin<br>Port: 9411:9411"]
    end
    
    subgraph "Host Machine"
        User["User Applications"]
        MCP["MCP Server (Node.js)"]
    end
    
    subgraph "External APIs"
        OpenAI["OpenAI API"]
    end
    
    User -->|"Calling Process"| MCP
    MCP -->|"http://localhost:8888"| FastAPI
    FastAPI -->|"http://qdrant:6333"| Qdrant
    FastAPI -->|"bolt://neo4j:7687"| Neo4j
    FastAPI -->|"API calls"| OpenAI
    FastAPI -->|"Telemetry"| OTEL
    OTEL -->|"Traces"| Zipkin
    
    classDef container fill:#d5e8d4,stroke:#82b366,stroke-width:2px;
    classDef external fill:#f8cecc,stroke:#b85450,stroke-width:2px;
    classDef host fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px;
    
    class FastAPI,Qdrant,Neo4j,OTEL,Zipkin container;
    class OpenAI external;
    class User,MCP host;
```

## Volume Mounts and Data Persistence

```mermaid
graph LR
    subgraph "Host File System"
        DataDir["./data/"]
        QdrantDir["./data/qdrant/"]
        HistoryDir["./data/history/"]
        Neo4jDir["./data/neo4j/"]
        FastAPIDir["./dgroo-fast-api/"]
    end
    
    subgraph "Docker Containers"
        QdrantContainer["Qdrant Container"]
        FastAPIContainer["FastAPI Container"]
        Neo4jContainer["Neo4j Container"]
    end
    
    QdrantDir -->|"Volume Mount<br>./data/qdrant:/qdrant/storage"| QdrantContainer
    HistoryDir -->|"Volume Mount<br>./data/history:/app/data/history"| FastAPIContainer
    FastAPIDir -->|"Volume Mount<br>./dgroo-fast-api:/app"| FastAPIContainer
    Neo4jDir -->|"Volume Mount<br>./data/neo4j:/data"| Neo4jContainer
    
    classDef host fill:#f5f5f5,stroke:#666,stroke-width:1px;
    classDef container fill:#d5e8d4,stroke:#82b366,stroke-width:2px;
    
    class DataDir,QdrantDir,HistoryDir,Neo4jDir,FastAPIDir host;
    class QdrantContainer,FastAPIContainer,Neo4jContainer container;
```