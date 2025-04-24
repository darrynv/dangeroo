# Detailed Mem0 Architecture

## Database Schemas

### Vector Store - ChromaDB

ChromaDB is the default vector database used for storing embeddings in Mem0. Here's a detailed view of its schema:

```mermaid
erDiagram
    COLLECTION ||--o{ EMBEDDING : contains
    COLLECTION {
        string name "memories"
        string dimension "1536 (OpenAI default)"
        boolean hnsw_enabled "If HNSW index used"
    }
    
    EMBEDDING {
        string id "UUID"
        vector embedding "Vector of floats"
        json metadata "Document metadata"
    }
    
    METADATA {
        string data "Actual memory content"
        string user_id "User identifier"
        string agent_id "Optional agent identifier"
        string run_id "Conversation identifier"
        string hash "MD5 hash of content"
        timestamp created_at "Creation timestamp"
        timestamp updated_at "Update timestamp"
    }
    
    EMBEDDING ||--|| METADATA : has
```

Alternatively, when using PGVector:

```mermaid
erDiagram
    MEMORIES {
        string id "UUID"
        vector embedding "Vector of floats (dimension 1536)"
        json metadata "Document metadata"
        timestamp created_at "Creation timestamp"
        timestamp updated_at "Update timestamp"
    }
    
    INDICES {
        string name "Index name"
        string type "HNSW or DiskANN"
        string column "embedding"
        string parameters "Index parameters"
    }
    
    MEMORIES }o--|| INDICES : indexed_by
```

### Graph Database - Neo4j

Neo4j is used for storing entities and relationships extracted from memories. Its schema:

```mermaid
graph TD
    subgraph Neo4j Schema
        Entity[Entity]
        Relationship[Relationship]
        
        Entity -->|has| EntityProps[Properties<br/>- name: string<br/>- type: string<br/>- embedding: vector<br/>- user_id: string<br/>- created: timestamp]
        
        Entity -->|RELATIONSHIP_TYPE| Entity
        Relationship -->|has| RelProps[Properties<br/>- type: string<br/>- created: timestamp<br/>- metadata: json]
    end
```

The Neo4j Cypher schema:

```cypher
// Entity node structure
CREATE (e:Entity {
  name: "entity_name",  // lowercase, spaces_as_underscores
  type: "entity_type",  // person, location, organization, etc.
  embedding: [...],     // vector representation
  user_id: "user123",   // associated user
  created: timestamp()  // creation time
})

// Relationship structure
CREATE (e1:Entity)-[:RELATIONSHIP_TYPE {
  created: timestamp(),
  metadata: {...}
}]->(e2:Entity)
```

### History Database - SQLite

SQLite is used for tracking the history of memory operations:

```mermaid
erDiagram
    MEMORY_HISTORY {
        string memory_id "UUID of the memory"
        string prev_value "Previous memory value"
        string new_value "New memory value"
        string operation "ADD, UPDATE, DELETE"
        timestamp created_at "Original creation time"
        timestamp updated_at "Update time"
        boolean is_deleted "Deletion flag"
    }
```

## Key Functions Flow

### add_memory Detailed Flow

```mermaid
flowchart TD
    Start[Client POST /memories] --> FastAPI[FastAPI Endpoint]
    FastAPI --> ValidateInput[Validate Input]
    ValidateInput --> MemoryAdd[Memory.add method]
    
    subgraph Memory Class
        MemoryAdd --> ProcessMessages[Process Messages]
        ProcessMessages --> GenerateEmbeddings[Generate Embeddings via OpenAI]
        
        GenerateEmbeddings --> ExtractFacts[Extract Facts via LLM]
        
        ExtractFacts --> ParallelOps[Parallel Operations]
        
        subgraph Vector Store Operations
            VectorStore[Add to Vector Store]
            VectorStore --> CheckDuplicates[Check for Similar Memories]
            CheckDuplicates --> DeDuplicate[De-duplicate if needed]
            DeDuplicate --> StoreVector[Store Vector in ChromaDB]
        end
        
        subgraph Graph Operations
            GraphStore[Add to Graph Store] 
            GraphStore --> ExtractEntities[Extract Entities via LLM]
            ExtractEntities --> ExtractRelationships[Extract Relationships]
            ExtractRelationships --> FindSimilarEntities[Find Similar Entities]
            FindSimilarEntities --> MergeEntities[Merge Similar Entities]
            MergeEntities --> StoreGraph[Store in Neo4j]
        end
        
        ParallelOps --> VectorStore
        ParallelOps --> GraphStore
        
        StoreVector --> RecordHistory[Record in History DB]
        StoreGraph --> RecordHistory
    end
    
    RecordHistory --> ReturnResults[Return Results]
    ReturnResults --> ClientResponse[Return to Client]
```

### search_memory Detailed Flow

```mermaid
flowchart TD
    Start[Client POST /search] --> FastAPI[FastAPI Endpoint]
    FastAPI --> ValidateInput[Validate Search Input]
    ValidateInput --> MemorySearch[Memory.search method]
    
    subgraph Memory Class
        MemorySearch --> ProcessQuery[Process Query]
        ProcessQuery --> GenerateEmbedding[Generate Query Embedding]
        
        GenerateEmbedding --> ParallelOps[Parallel Operations]
        
        subgraph Vector Search
            VectorSearch[Search Vector Store]
            VectorSearch --> ApplyFilters[Apply User/Agent Filters]
            ApplyFilters --> PerformVectorSimilarity[Perform Vector Similarity]
            PerformVectorSimilarity --> RankVectorResults[Rank Vector Results]
        end
        
        subgraph Graph Search
            GraphSearch[Search Graph Store]
            GraphSearch --> ExtractQueryEntities[Extract Entities from Query]
            ExtractQueryEntities --> FindSimilarNodes[Find Similar Entity Nodes]
            FindSimilarNodes --> TraverseRelationships[Traverse Relationships]
            TraverseRelationships --> RankGraphResults[Rank Graph Results]
        end
        
        ParallelOps --> VectorSearch
        ParallelOps --> GraphSearch
        
        RankVectorResults --> CombineResults[Combine Results]
        RankGraphResults --> CombineResults
        
        CombineResults --> FinalRanking[Final Result Ranking]
    end
    
    FinalRanking --> FormatResults[Format Results]
    FormatResults --> ClientResponse[Return to Client]
```

## API Endpoints 

```mermaid
graph TD
    subgraph "FastAPI Endpoints"
        config["/configure - Set configuration"]
        add["/memories - Create memories"]
        getAll["/memories - Get all memories"]
        getOne["/memories/{id} - Get specific memory"]
        search["/search - Search memories"]
        update["/memories/{id} - Update memory"]
        history["/memories/{id}/history - Get memory history"]
        delete["/memories/{id} - Delete memory"]
        deleteAll["/memories - Delete all memories"]
        reset["/reset - Reset all memories"]
        health["/health - Health check"]
        debug["/debug - Debug information"]
    end
    
    MEMORY[Memory Class] --> config
    MEMORY --> add
    MEMORY --> getAll
    MEMORY --> getOne
    MEMORY --> search
    MEMORY --> update
    MEMORY --> history
    MEMORY --> delete
    MEMORY --> deleteAll
    MEMORY --> reset
```

## OpenAI Integration

```mermaid
flowchart LR
    subgraph "Mem0 Components"
        Memory[Memory Manager]
        EmbeddingService[Embedding Service]
        LLMService[LLM Service]
    end
    
    subgraph "OpenAI API"
        EmbeddingAPI[Embeddings API]
        CompletionAPI[Completion API]
    end
    
    Memory --> EmbeddingService
    Memory --> LLMService
    
    EmbeddingService -->|"text-embedding-3-small<br/>1536-dimension vectors"| EmbeddingAPI
    LLMService -->|"gpt-4o<br/>Structured Output"| CompletionAPI
    
    EmbeddingAPI -->|"Vector Embeddings"| EmbeddingService
    CompletionAPI -->|"Facts, Entities,<br/>Relationships"| LLMService
```

## ChromaDB Storage Structure

```mermaid
graph TD
    subgraph "ChromaDB"
        Collection[Collection: "memories"]
        
        subgraph "Documents"
            Doc1[Document 1]
            Doc2[Document 2]
            DocN[Document N]
        end
        
        Collection --> Doc1
        Collection --> Doc2
        Collection --> DocN
        
        Doc1 --> ID1[id: UUID]
        Doc1 --> Embedding1[embedding: Vector]
        Doc1 --> Metadata1[metadata: JSON]
        
        Metadata1 --> Content1[data: Text content]
        Metadata1 --> UserID1[user_id: User identifier]
        Metadata1 --> AgentID1[agent_id: Agent identifier]
        Metadata1 --> RunID1[run_id: Conversation ID]
        Metadata1 --> Hash1[hash: Content hash]
        Metadata1 --> Created1[created_at: Timestamp]
        Metadata1 --> Updated1[updated_at: Timestamp]
    end
```

## Neo4j Graph Model

```mermaid
graph TD
    subgraph "Neo4j Graph Database"
        Person1[Person: Alice]
        Person2[Person: Bob]
        Company[Organization: Acme]
        Location[Location: New York]
        Concept[Concept: Machine Learning]
        
        Person1 -->|WORKS_AT| Company
        Person2 -->|WORKS_AT| Company
        Person1 -->|KNOWS| Person2
        Person1 -->|LOCATED_IN| Location
        Person2 -->|INTERESTED_IN| Concept
        Company -->|LOCATED_IN| Location
    end
    
    subgraph "Entity Properties"
        EntityProps[Entity Node Properties<br/>- name: lowercase_name<br/>- type: entity_type<br/>- embedding: vector<br/>- user_id: user_identifier<br/>- created: timestamp]
    end
    
    subgraph "Relationship Properties"
        RelProps[Relationship Properties<br/>- type: relationship_type<br/>- created: timestamp<br/>- context: text]
    end
    
    Person1 -.-> EntityProps
    Person1 -->|KNOWS| Person2
    Person1 -->|RELATIONSHIP| EntityProps
```

## Mem0 Internal Factory Architecture

```mermaid
graph TD
    subgraph "Memory Factory"
        MemoryFactory[Memory.from_config]
        AsyncMemoryFactory[AsyncMemory.from_config]
    end
    
    subgraph "Component Factories"
        VectorStoreFactory[VectorStoreFactory]
        EmbeddingFactory[EmbeddingFactory]
        LLMFactory[LLMFactory]
        GraphFactory[GraphFactory]
    end
    
    subgraph "Vector Store Implementations"
        ChromaDBImpl[ChromaDB]
        PGVectorImpl[PGVector]
        FAISS[FAISS]
        Weaviate[Weaviate]
    end
    
    subgraph "Embedding Implementations"
        OpenAIEmbedding[OpenAI Embeddings]
        HuggingFaceEmbedding[HuggingFace Embeddings]
        AzureOpenAIEmbedding[Azure OpenAI Embeddings]
    end
    
    subgraph "LLM Implementations"
        OpenAILLM[OpenAI LLM]
        AnthropicLLM[Anthropic LLM]
        AzureOpenAILLM[Azure OpenAI LLM]
    end
    
    MemoryFactory --> VectorStoreFactory
    MemoryFactory --> EmbeddingFactory
    MemoryFactory --> LLMFactory
    MemoryFactory --> GraphFactory
    
    AsyncMemoryFactory --> VectorStoreFactory
    AsyncMemoryFactory --> EmbeddingFactory
    AsyncMemoryFactory --> LLMFactory
    AsyncMemoryFactory --> GraphFactory
    
    VectorStoreFactory --> ChromaDBImpl
    VectorStoreFactory --> PGVectorImpl
    VectorStoreFactory --> FAISS
    VectorStoreFactory --> Weaviate
    
    EmbeddingFactory --> OpenAIEmbedding
    EmbeddingFactory --> HuggingFaceEmbedding
    EmbeddingFactory --> AzureOpenAIEmbedding
    
    LLMFactory --> OpenAILLM
    LLMFactory --> AnthropicLLM
    LLMFactory --> AzureOpenAILLM
```