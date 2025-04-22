# Mem0 MCP Server Architecture Diagrams

## System Architecture Diagram

```mermaid
graph TD
    Client[Client Application] --> FastAPI[FastAPI Service]
    FastAPI --> Memory[Memory Manager]
    Memory -- Embeddings --> OpenAI[OpenAI API]
    Memory -- Vector Storage --> ChromaDB
    Memory -- Graph Storage --> Neo4j
    Memory -- History --> SQLite
    
    subgraph Memory Operations
        Add[add_memory]
        Search[search_memory]
        Get[get_memory]
        Update[update_memory]
        Delete[delete_memory]
    end
    
    FastAPI --> Add
    FastAPI --> Search
    FastAPI --> Get
    FastAPI --> Update
    FastAPI --> Delete
```

## C4 Component Diagram

```mermaid
graph TB
    subgraph Client Layer
        Client[Client Application]
    end
    
    subgraph API Layer
        FastAPI[FastAPI Service]
    end
    
    subgraph Core Layer
        Memory[Memory Manager]
        Memory --> VectorStore[Vector Store Adapter]
        Memory --> GraphStore[Graph Store Adapter]
        Memory --> EmbeddingModel[Embedding Model]
        Memory --> LLMService[LLM Service]
        Memory --> HistoryStore[History Store]
    end
    
    subgraph Data Storage Layer
        ChromaDB[ChromaDB Vector Database]
        Neo4j[Neo4j Graph Database]
        SQLite[SQLite History Database]
    end
    
    subgraph External Services
        OpenAIAPI[OpenAI API]
    end
    
    Client --> FastAPI
    FastAPI --> Memory
    
    VectorStore --> ChromaDB
    GraphStore --> Neo4j
    HistoryStore --> SQLite
    EmbeddingModel --> OpenAIAPI
    LLMService --> OpenAIAPI
```

## Database Schema

```mermaid
erDiagram
    MEMORY {
        string id
        vector embedding
        string data
        string user_id
        string agent_id
        string run_id
        string hash
        timestamp created_at
        timestamp updated_at
    }
    
    ENTITY {
        string name
        string type
        vector embedding
        string user_id
        timestamp created
    }
    
    RELATIONSHIP {
        string type
        timestamp created
    }
    
    HISTORY {
        string memory_id
        string prev_value
        string new_value
        string operation
        timestamp created_at
        timestamp updated_at
        boolean is_deleted
    }
    
    ENTITY ||--o{ RELATIONSHIP : has
    RELATIONSHIP }o--|| ENTITY : connects_to
    MEMORY ||--o{ HISTORY : tracks
```

## add_memory Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Memory
    participant OpenAI
    participant ChromaDB
    participant Neo4j
    participant SQLite
    
    Client->>FastAPI: POST /memories (messages)
    FastAPI->>Memory: add(messages, user_id, agent_id)
    
    Memory->>OpenAI: Generate embeddings
    OpenAI->>Memory: Return embeddings
    
    Memory->>OpenAI: Extract facts from messages
    OpenAI->>Memory: Return structured facts
    
    par Vector Storage
        Memory->>ChromaDB: Insert vectors and metadata
        ChromaDB->>Memory: Confirm storage
    and Graph Storage
        Memory->>OpenAI: Extract entities and relationships
        OpenAI->>Memory: Return structured entities
        Memory->>Neo4j: Create/update nodes and relationships
        Neo4j->>Memory: Confirm graph updates
    end
    
    Memory->>SQLite: Record memory history
    Memory->>FastAPI: Return memory IDs and status
    FastAPI->>Client: Return API response
```

## search_memory Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Memory
    participant OpenAI
    participant ChromaDB
    participant Neo4j
    
    Client->>FastAPI: POST /search (query)
    FastAPI->>Memory: search(query, filters)
    
    Memory->>OpenAI: Generate embedding for query
    OpenAI->>Memory: Return query embedding
    
    par Vector Search
        Memory->>ChromaDB: Search for similar vectors
        ChromaDB->>Memory: Return matching memories
    and Graph Search
        Memory->>OpenAI: Extract entities from query
        OpenAI->>Memory: Return structured entities
        Memory->>Neo4j: Search for entity relationships
        Neo4j->>Memory: Return related entities
    end
    
    Memory->>Memory: Combine and rank results
    Memory->>FastAPI: Return combined search results
    FastAPI->>Client: Return API response
```

## Vector Store Architecture (PGVector Variant)

```mermaid
graph TD
    subgraph Vector Store Module
        PGVector[PGVector Adapter]
        PGVector --> PSQL[(PostgreSQL + pgvector)]
    end
    
    subgraph PGVector Internals
        VectorTable[Memories Table]
        VectorTable --> VectorColumn[Vector Column]
        VectorTable --> MetadataColumns[Metadata Columns]
        VectorColumn --> VectorIndex[Vector Index]
    end
    
    subgraph Search Operations
        CosineDistance[Cosine Distance]
        HNSWIndex[HNSW Index]
        DiskANNIndex[DiskANN Index]
    end
    
    Memory --> PGVector
    PSQL --> VectorTable
    VectorColumn --> CosineDistance
    VectorIndex --> HNSWIndex
    VectorIndex --> DiskANNIndex
```

## Neo4j Graph Memory

```mermaid
graph TD
    subgraph Graph Memory Module
        MemoryGraph[Memory Graph]
        MemoryGraph --> Neo4jDB[(Neo4j Database)]
    end
    
    subgraph Graph Entities
        EntityNode[Entity Nodes]
        RelationshipEdge[Relationship Edges]
        EntityNode --> EntityEmbedding[Entity Embedding Vector]
        EntityNode --> EntityProperties[Entity Properties]
        RelationshipEdge --> RelationshipProperties[Relationship Properties]
    end
    
    subgraph Graph Operations
        EntityExtraction[Entity Extraction]
        RelationshipExtraction[Relationship Extraction]
        EntityMerging[Entity Merging]
        SimilaritySearch[Similarity Search]
    end
    
    Memory --> MemoryGraph
    Neo4jDB --> EntityNode
    Neo4jDB --> RelationshipEdge
    EntityExtraction --> OpenAI
    RelationshipExtraction --> OpenAI
    EntityNode --> SimilaritySearch
    EntityNode --> EntityMerging
```

## System Layered Architecture

```mermaid
flowchart TB
    subgraph Presentation Layer
        FastAPI
        HTTPEndpoints[REST Endpoints]
        FastAPI --> HTTPEndpoints
    end
    
    subgraph Core Domain Layer
        MemoryManager[Memory Manager]
        AddMemory[Add Memory]
        SearchMemory[Search Memory]
        UpdateMemory[Update Memory]
        DeleteMemory[Delete Memory]
        
        MemoryManager --> AddMemory
        MemoryManager --> SearchMemory
        MemoryManager --> UpdateMemory
        MemoryManager --> DeleteMemory
    end
    
    subgraph Infrastructure Layer
        VectorStoreService[Vector Store Service]
        GraphStoreService[Graph Store Service]
        LLMService[LLM Service]
        EmbeddingsService[Embeddings Service]
        HistoryService[History Service]
    end
    
    subgraph External Resources
        ChromaDBService[ChromaDB]
        Neo4jService[Neo4j]
        SQLiteService[SQLite]
        OpenAIService[OpenAI API]
    end
    
    HTTPEndpoints --> MemoryManager
    AddMemory --> VectorStoreService
    AddMemory --> GraphStoreService
    AddMemory --> LLMService
    AddMemory --> EmbeddingsService
    AddMemory --> HistoryService
    SearchMemory --> VectorStoreService
    SearchMemory --> GraphStoreService
    SearchMemory --> EmbeddingsService
    
    VectorStoreService --> ChromaDBService
    GraphStoreService --> Neo4jService
    HistoryService --> SQLiteService
    LLMService --> OpenAIService
    EmbeddingsService --> OpenAIService
```