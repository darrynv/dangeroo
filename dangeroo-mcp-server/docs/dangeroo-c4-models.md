# Dangeroo Mem0 MCP Server C4 Models

This document provides C4 model diagrams for the Dangeroo Mem0 MCP Server. C4 models offer different levels of abstraction to help understand the system architecture.

## Level 1: System Context Diagram

```mermaid
C4Context
    title System Context diagram for Dangeroo Mem0 MCP Server

    Person(user, "User", "A user interacting with Claude")
    
    System(claudeSystem, "Claude AI", "Claude language model with MCP capabilities")
    
    System_Boundary(dangerooSystem, "Dangeroo Mem0 MCP System") {
        System(mcpServer, "MCP Server", "Routes tool calls to memory services")
        System(memoryBackend, "Memory Backend", "Stores and retrieves memories")
    }

    System_Ext(openAI, "OpenAI API", "Provides embeddings and LLM capabilities")
    
    Rel(user, claudeSystem, "Interacts with")
    Rel(claudeSystem, mcpServer, "Makes tool calls to", "MCP Protocol")
    Rel(mcpServer, memoryBackend, "Routes requests to", "HTTP/REST")
    Rel(memoryBackend, openAI, "Uses for embeddings and LLM", "HTTP/REST")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Level 2: Container Diagram

```mermaid
C4Container
    title Container diagram for Dangeroo Mem0 MCP Server

    Person(user, "User", "A user interacting with Claude")
    
    System(claudeSystem, "Claude AI", "Claude language model with MCP capabilities")
    
    System_Boundary(dangerooSystem, "Dangeroo Mem0 MCP System") {
        Container(mcpNodeServer, "MCP Server", "Node.js", "Handles Claude's MCP tool calls")
        
        Container_Boundary(backendServices, "Memory Backend Services") {
            Container(fastApi, "FastAPI Service", "Python", "Provides memory API endpoints")
            ContainerDb(chroma, "ChromaDB", "Vector Database", "Stores vector embeddings for semantic search")
            ContainerDb(neo4j, "Neo4j", "Graph Database", "Stores entity relationships")
            ContainerDb(sqlite, "SQLite", "History Database", "Tracks memory changes")
        }
        
        Container(telemetry, "OpenTelemetry", "Collector", "Collects system metrics and traces")
        Container(zipkin, "Zipkin", "Monitoring UI", "Visualizes system traces")
    }
    
    System_Ext(openAI, "OpenAI API", "Provides embeddings and LLM capabilities")
    
    Rel(user, claudeSystem, "Interacts with")
    Rel(claudeSystem, mcpNodeServer, "Makes tool calls to", "MCP Protocol")
    Rel(mcpNodeServer, fastApi, "Sends requests to", "HTTP/REST")
    
    Rel(fastApi, chroma, "Stores and queries vectors in", "HTTP")
    Rel(fastApi, neo4j, "Stores and queries graphs in", "Bolt protocol")
    Rel(fastApi, sqlite, "Logs history in", "SQLite connection")
    
    Rel(fastApi, openAI, "Uses for embeddings and LLM", "HTTP/REST")
    Rel(fastApi, telemetry, "Reports metrics to", "gRPC")
    Rel(telemetry, zipkin, "Forwards traces to", "HTTP")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Level 3: Component Diagram for MCP Server

```mermaid
C4Component
    title Component diagram for MCP Server

    Person(user, "User", "A user interacting with Claude")
    System(claudeSystem, "Claude AI", "Claude language model with MCP capabilities")
    
    Container_Boundary(mcpServer, "MCP Server") {
        Component(serverCore, "Server Core", "TypeScript", "Core MCP server implementation")
        Component(toolHandlers, "Tool Handlers", "TypeScript", "Handles MCP tool requests")
        Component(localApiClient, "Local API Client", "TypeScript", "Client for FastAPI service")
        Component(storageManager, "Storage Manager", "TypeScript", "Manages different storage modes")
    }
    
    Container(fastApi, "FastAPI Service", "Provides memory API endpoints")
    
    Rel(user, claudeSystem, "Interacts with")
    Rel(claudeSystem, serverCore, "Makes tool calls to", "MCP Protocol")
    
    Rel(serverCore, toolHandlers, "Delegates requests to")
    Rel(toolHandlers, storageManager, "Uses")
    Rel(storageManager, localApiClient, "Uses in local mode")
    
    Rel(localApiClient, fastApi, "Sends requests to", "HTTP/REST")

    UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

## Level 3: Component Diagram for FastAPI Service

```mermaid
C4Component
    title Component diagram for FastAPI Service

    Container(mcpServer, "MCP Server", "Handles Claude's MCP tool calls")
    System_Ext(openAI, "OpenAI API", "Provides embeddings and LLM capabilities")
    
    Container_Boundary(fastApiService, "FastAPI Service") {
        Component(apiRoutes, "API Routes", "Python", "REST API endpoints")
        Component(memoryManager, "Memory Manager", "Python", "Core memory operations")
        Component(vectorStore, "Vector Store Client", "Python", "ChromaDB integration")
        Component(graphStore, "Graph Store Client", "Python", "Neo4j integration")
        Component(embedder, "Embedding Client", "Python", "Handles embeddings")
        Component(llmClient, "LLM Client", "Python", "Handles LLM operations")
        Component(historyTracker, "History Tracker", "Python", "Tracks memory changes")
    }
    
    ContainerDb(chroma, "ChromaDB", "Vector Database")
    ContainerDb(neo4j, "Neo4j", "Graph Database")
    ContainerDb(sqlite, "SQLite", "History Database")
    
    Rel(mcpServer, apiRoutes, "Sends requests to", "HTTP/REST")
    
    Rel(apiRoutes, memoryManager, "Uses")
    Rel(memoryManager, vectorStore, "Uses for vector operations")
    Rel(memoryManager, graphStore, "Uses for graph operations")
    Rel(memoryManager, embedder, "Uses for embeddings")
    Rel(memoryManager, llmClient, "Uses for LLM operations")
    Rel(memoryManager, historyTracker, "Uses for history tracking")
    
    Rel(vectorStore, chroma, "Stores and queries vectors in", "HTTP")
    Rel(graphStore, neo4j, "Stores and queries graphs in", "Bolt protocol")
    Rel(historyTracker, sqlite, "Logs history in", "SQLite connection")
    
    Rel(embedder, openAI, "Gets embeddings from", "HTTP/REST")
    Rel(llmClient, openAI, "Gets completions from", "HTTP/REST")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## Level 4: Code Diagram for MCP Tool Handling

```mermaid
classDiagram
    class Server {
        +connect(transport)
        +setRequestHandler()
        +close()
    }
    
    class StdioServerTransport {
        +constructor()
    }
    
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
        -handleAddMemory(args)
        -handleSearchMemory(args)
        -handleDeleteMemory(args)
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
    
    Mem0MCPServer --> Server : uses
    Mem0MCPServer --> StdioServerTransport : connects with
    Mem0MCPServer --> StorageMode : has
    Mem0MCPServer --> LocalApiClient : may use
```

## Level 4: Code Diagram for Memory Operations

```mermaid
classDiagram
    class Memory {
        +from_config(config)
        +add(messages, **kwargs)
        +search(query, **kwargs)
        +get(memory_id)
        +get_all(**kwargs)
        +update(memory_id, data)
        +delete(memory_id)
        +delete_all(**kwargs)
        +reset()
        +history(memory_id)
    }
    
    class VectorStore {
        +store_vectors(vectors)
        +search_vectors(query_vector)
        +delete_vectors(ids)
        +reset()
    }
    
    class GraphStore {
        +store_entities(entities)
        +store_relationships(relationships)
        +search_entities(query)
        +delete_entity(entity_id)
        +reset()
    }
    
    class EmbeddingProvider {
        +get_embeddings(texts)
    }
    
    class LLMProvider {
        +extract_facts(text)
        +complete(prompt)
    }
    
    class HistoryTracker {
        +log_change(memory_id, operation, data)
        +get_history(memory_id)
    }
    
    Memory --> VectorStore : uses
    Memory --> GraphStore : uses
    Memory --> EmbeddingProvider : uses
    Memory --> LLMProvider : uses
    Memory --> HistoryTracker : uses
```

## Level 4: Code Diagram for FastAPI Endpoints

```mermaid
classDiagram
    class FastAPI {
        +post(path)
        +get(path)
        +put(path)
        +delete(path)
    }
    
    class MemoryCreate {
        +messages: List[Message]
        +user_id: Optional[str]
        +agent_id: Optional[str]
        +run_id: Optional[str]
        +metadata: Optional[Dict]
    }
    
    class SearchRequest {
        +query: str
        +user_id: Optional[str]
        +run_id: Optional[str]
        +agent_id: Optional[str]
        +filters: Optional[Dict]
    }
    
    class Message {
        +role: str
        +content: str
    }
    
    class Endpoints {
        +set_config(config)
        +add_memory(memory_create)
        +get_all_memories(user_id, run_id, agent_id)
        +get_memory(memory_id)
        +search_memories(search_req)
        +update_memory(memory_id, updated_memory)
        +memory_history(memory_id)
        +delete_memory(memory_id)
        +delete_all_memories(user_id, run_id, agent_id)
        +reset_memory()
        +health_check()
        +debug_info()
    }
    
    FastAPI --> Endpoints : defines
    Endpoints --> MemoryCreate : uses
    Endpoints --> SearchRequest : uses
    MemoryCreate --> Message : contains
```

## Data Model Diagrams

### ChromaDB Collection Data Model

```mermaid
classDiagram
    class ChromaCollection {
        +add(embeddings, metadatas, documents, ids)
        +query(query_embeddings, n_results, where)
        +get(ids, where)
        +delete(ids, where)
        +count()
    }
    
    class MemoryDocument {
        +id: str
        +embedding: List[float]
        +document: str
        +metadata: Dict
    }
    
    class MemoryMetadata {
        +memory_id: str
        +user_id: str
        +run_id: Optional[str]
        +agent_id: Optional[str]
        +custom_metadata: Optional[Dict]
        +created_at: datetime
        +updated_at: datetime
    }
    
    ChromaCollection -- MemoryDocument : contains
    MemoryDocument -- MemoryMetadata : has
```

### Neo4j Graph Data Model

```mermaid
classDiagram
    class GraphDatabase {
        +run_query(query, parameters)
    }
    
    class Entity {
        +id: str
        +name: str
        +type: str
        +properties: Dict
    }
    
    class Relationship {
        +id: str
        +type: str
        +source_id: str
        +target_id: str
        +properties: Dict
    }
    
    class MemoryNode {
        +id: str
        +user_id: str
        +run_id: Optional[str]
        +agent_id: Optional[str]
        +created_at: datetime
    }
    
    GraphDatabase -- Entity : contains
    GraphDatabase -- Relationship : contains
    GraphDatabase -- MemoryNode : contains
    MemoryNode -- Entity : CONTAINS
    Entity -- Relationship : participates in
```

### MCP Tool Request/Response Models

```mermaid
classDiagram
    class Mem0AddToolArgs {
        +content: string
        +userId: string
        +sessionId?: string
        +agentId?: string
        +metadata?: Record<string, any>
    }
    
    class Mem0SearchToolArgs {
        +query: string
        +userId: string
        +sessionId?: string
        +agentId?: string
        +filters?: Record<string, any>
        +threshold?: number
    }
    
    class Mem0DeleteToolArgs {
        +memoryId: string
        +userId: string
        +sessionId?: string
        +agentId?: string
    }
    
    class Mem0Message {
        +role: "user" | "assistant" | "system"
        +content: string
    }
    
    class ToolResponse {
        +content: ContentItem[]
    }
    
    class ContentItem {
        +type: "text"
        +text: string
    }
    
    Mem0AddToolArgs --> Mem0Message : creates
    ToolResponse --> ContentItem : contains
```