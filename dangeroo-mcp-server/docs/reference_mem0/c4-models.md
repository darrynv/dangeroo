# C4 Models for Mem0 Architecture

## C4 Context Diagram

```mermaid
C4Context
    title System Context diagram for Mem0 Memory System
    
    Person(client, "Client Application", "Application using Mem0 for memory storage and retrieval")
    
    System(mem0, "Mem0 Memory System", "Stores, retrieves, and manages semantic memories for AI applications")
    
    System_Ext(openai, "OpenAI API", "Provides embeddings and LLM capabilities for memory processing")
    
    Rel(client, mem0, "Uses", "REST API")
    Rel(mem0, openai, "Uses", "HTTP API")
    
    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## C4 Container Diagram

```mermaid
C4Container
    title Container diagram for Mem0 Memory System
    
    Person(client, "Client Application", "Application using Mem0 for memory storage and retrieval")
    
    System_Boundary(mem0, "Mem0 Memory System") {
        Container(fastapi, "FastAPI Service", "Python/FastAPI", "Provides REST API endpoints for memory operations")
        Container(memory_manager, "Memory Manager", "Python", "Core component that orchestrates memory operations")
        
        ContainerDb(chroma, "ChromaDB", "Vector Database", "Stores vector embeddings for semantic search")
        ContainerDb(neo4j, "Neo4j", "Graph Database", "Stores entities and relationships")
        ContainerDb(sqlite, "SQLite", "Relational Database", "Stores memory operation history")
    }
    
    System_Ext(openai, "OpenAI API", "Provides embeddings and LLM capabilities")
    
    Rel(client, fastapi, "Uses", "REST API")
    Rel(fastapi, memory_manager, "Uses", "Direct call")
    Rel(memory_manager, chroma, "Reads/Writes", "ChromaDB Client")
    Rel(memory_manager, neo4j, "Reads/Writes", "Neo4j Bolt Protocol")
    Rel(memory_manager, sqlite, "Reads/Writes", "SQLite Connection")
    Rel(memory_manager, openai, "Uses", "HTTP API")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## C4 Component Diagram (Memory Manager)

```mermaid
C4Component
    title Component diagram for Memory Manager
    
    Container_Boundary(memory_manager, "Memory Manager") {
        Component(memory_class, "Memory Class", "Python", "Central orchestrator for memory operations")
        Component(vector_adapter, "Vector Store Adapter", "Python", "Abstracts vector database operations")
        Component(graph_adapter, "Graph Store Adapter", "Python", "Abstracts graph database operations")
        Component(embedding_service, "Embedding Service", "Python", "Handles text-to-vector conversions")
        Component(llm_service, "LLM Service", "Python", "Handles AI inference operations")
        Component(history_service, "History Service", "Python", "Tracks memory changes")
    }
    
    Container(fastapi, "FastAPI Service", "Python/FastAPI", "API Gateway")
    ContainerDb(chroma, "ChromaDB", "Vector Database", "Stores embeddings")
    ContainerDb(neo4j, "Neo4j", "Graph Database", "Stores relationships")
    ContainerDb(sqlite, "SQLite", "Relational DB", "Stores history")
    System_Ext(openai, "OpenAI API", "AI Services")
    
    Rel(fastapi, memory_class, "Uses", "Direct call")
    
    Rel(memory_class, vector_adapter, "Uses", "Method call")
    Rel(memory_class, graph_adapter, "Uses", "Method call")
    Rel(memory_class, embedding_service, "Uses", "Method call")
    Rel(memory_class, llm_service, "Uses", "Method call")
    Rel(memory_class, history_service, "Uses", "Method call")
    
    Rel(vector_adapter, chroma, "Reads/Writes", "Client API")
    Rel(graph_adapter, neo4j, "Reads/Writes", "Bolt Protocol")
    Rel(history_service, sqlite, "Reads/Writes", "SQL")
    Rel(embedding_service, openai, "Requests embeddings", "HTTP API")
    Rel(llm_service, openai, "Requests completions", "HTTP API")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## C4 Code Diagram (add_memory)

```mermaid
C4Dynamic
    title Dynamic diagram for add_memory operation
    
    Person(client, "Client Application", "Application using Mem0")
    
    Container(fastapi, "FastAPI", "API Gateway")
    Container(memory_manager, "Memory Manager", "Core component")
    ContainerDb(chroma, "ChromaDB", "Vector Database")
    ContainerDb(neo4j, "Neo4j", "Graph Database")
    ContainerDb(sqlite, "SQLite", "History Database")
    System_Ext(openai, "OpenAI API", "AI Services")
    
    Rel(client, fastapi, "1. POST /memories", "Messages + Metadata")
    Rel(fastapi, memory_manager, "2. add(messages, **params)")
    Rel(memory_manager, openai, "3. Generate embeddings")
    Rel(openai, memory_manager, "4. Return embeddings")
    Rel(memory_manager, openai, "5. Extract facts from messages")
    Rel(openai, memory_manager, "6. Return structured facts")
    
    Rel(memory_manager, chroma, "7a. Insert vectors and metadata")
    Rel(chroma, memory_manager, "8a. Confirm storage")
    
    Rel(memory_manager, openai, "7b. Extract entities and relationships")
    Rel(openai, memory_manager, "8b. Return structured entities")
    Rel(memory_manager, neo4j, "9b. Create nodes and relationships")
    Rel(neo4j, memory_manager, "10b. Confirm graph updates")
    
    Rel(memory_manager, sqlite, "11. Record history")
    Rel(memory_manager, fastapi, "12. Return memory IDs")
    Rel(fastapi, client, "13. Return API response")
    
    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

## C4 Dynamic Diagram (search_memory)

```mermaid
C4Dynamic
    title Dynamic diagram for search_memory operation
    
    Person(client, "Client Application", "Application using Mem0")
    
    Container(fastapi, "FastAPI", "API Gateway")
    Container(memory_manager, "Memory Manager", "Core component")
    ContainerDb(chroma, "ChromaDB", "Vector Database")
    ContainerDb(neo4j, "Neo4j", "Graph Database")
    System_Ext(openai, "OpenAI API", "AI Services")
    
    Rel(client, fastapi, "1. POST /search", "Query + Filters")
    Rel(fastapi, memory_manager, "2. search(query, **filters)")
    Rel(memory_manager, openai, "3. Generate embedding for query")
    Rel(openai, memory_manager, "4. Return query embedding")
    
    Rel(memory_manager, chroma, "5a. Search for similar vectors")
    Rel(chroma, memory_manager, "6a. Return matching memories")
    
    Rel(memory_manager, openai, "5b. Extract entities from query")
    Rel(openai, memory_manager, "6b. Return structured entities")
    Rel(memory_manager, neo4j, "7b. Search for entity relationships")
    Rel(neo4j, memory_manager, "8b. Return related entities")
    
    Rel(memory_manager, memory_manager, "9. Combine and rank results")
    Rel(memory_manager, fastapi, "10. Return combined results")
    Rel(fastapi, client, "11. Return API response")
    
    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

## C4 Deployment Diagram

```mermaid
C4Deployment
    title Deployment diagram for Mem0 Memory System
    
    Deployment_Node(cloud, "Cloud Provider") {
        Deployment_Node(app_server, "Application Server") {
            Container(fastapi, "FastAPI Service", "Python/FastAPI", "Provides REST API endpoints")
            Container(memory_manager, "Memory Manager", "Python", "Core component")
        }
        
        Deployment_Node(db_server, "Database Server") {
            ContainerDb(chroma, "ChromaDB", "Vector Database", "Stores embeddings")
            ContainerDb(neo4j, "Neo4j", "Graph Database", "Stores relationships")
            ContainerDb(sqlite, "SQLite", "Relational DB", "Stores history")
        }
    }
    
    System_Ext(openai, "OpenAI API", "AI Services")
    Person(client, "Client Application", "Uses Mem0 services")
    
    Rel(client, fastapi, "Uses", "HTTPS")
    
    Rel(fastapi, memory_manager, "Uses", "Local call")
    Rel(memory_manager, chroma, "Connects to", "TCP/IP")
    Rel(memory_manager, neo4j, "Connects to", "Bolt Protocol")
    Rel(memory_manager, sqlite, "Connects to", "File access")
    Rel(memory_manager, openai, "Uses", "HTTPS")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```