import os
import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from mem0 import Memory, AsyncMemory
from dotenv import load_dotenv
from qdrant_client.http.models import CollectionInfo # Add this import

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

# ChromaDB configuration
#CHROMA_HOST = os.environ.get("CHROMA_HOST", "chroma")
#CHROMA_PORT = os.environ.get("CHROMA_PORT", "8000")
#CHROMA_COLLECTION_NAME = os.environ.get("CHROMA_COLLECTION_NAME", "memories")
#CHROMA_PATH = os.environ.get("CHROMA_PATH", "/app/data/chroma")

QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant")
QDRANT_PORT = os.environ.get("QDRANT_PORT", "6333")
QDRANT_COLLECTION_NAME = os.environ.get("QDRANT_COLLECTION_NAME", "memories")
QDRANT_ONDISK = os.environ.get("QDRANT_ONDISK", "False").lower() == "true"
QDRANT_PATH = os.environ.get("QDRANT_PATH", "/qdrant/storage")

# Neo4j configuration
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "mem0graph")

# Other configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY not set! Memory operations will fail.")

HISTORY_DB_PATH = os.environ.get("HISTORY_DB_PATH", "/app/data/history/history.db")

DEFAULT_CONFIG = {
    "version": "v1.1",
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": QDRANT_COLLECTION_NAME,  # default
            "embedding_model_dims": 1536,  # default
            "host": QDRANT_HOST,
            "port": 6333,
            "path": QDRANT_PATH,
            "url": None,
            "api_key": None,
            "on_disk": QDRANT_ONDISK
        }
 #       "provider": "chroma",
 #       "config": {
 #           "host": CHROMA_HOST,
 #           "port": int(CHROMA_PORT),
 #           "collection_name": CHROMA_COLLECTION_NAME,
#           "persist_directory": CHROMA_PATH,
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URI,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "temperature": 0.2,
            "model": "gpt-4o"
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small",
            "embedding_dims": 1536,
        }
    },
    "history_db_path": HISTORY_DB_PATH,
}

try:
    MEMORY_INSTANCE = Memory.from_config(DEFAULT_CONFIG)
    logging.info("Memory instance initialized successfully")
except Exception as e:
    logging.error(f"Error initializing memory instance: {e}")
    MEMORY_INSTANCE = None

app = FastAPI(
    title="Dangeroo Mem0 REST APIs",
    description="A REST API for managing and searching memories for your AI Agents and Apps.",
    version="1.0.0",
)


class Message(BaseModel):
    role: str = Field(..., description="Role of the message (user or assistant).")
    content: str = Field(..., description="Message content.")


class MemoryCreate(BaseModel):
    messages: List[Message] = Field(..., description="List of messages to store.")
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    run_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query.")
    user_id: Optional[str] = None
    run_id: Optional[str] = None
    agent_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None


@app.post("/configure", summary="Configure Mem0")
def set_config(config: Dict[str, Any]):
    """Set memory configuration."""
    global MEMORY_INSTANCE
    try:
        MEMORY_INSTANCE = Memory.from_config(config)
        return {"message": "Configuration set successfully"}
    except Exception as e:
        logging.exception(f"Error setting configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memories", summary="Create memories")
def add_memory(memory_create: MemoryCreate):
    """Store new memories."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    if not any([memory_create.user_id, memory_create.agent_id, memory_create.run_id]):
        raise HTTPException(
            status_code=400, detail="At least one identifier (user_id, agent_id, run_id) is required."
        )

    params = {k: v for k, v in memory_create.model_dump().items() if v is not None and k != "messages"}
    messages_to_add = [m.model_dump() for m in memory_create.messages]
    logging.info(f"Attempting to add memory with params: {params} and messages: {messages_to_add}")
    try:
        response = MEMORY_INSTANCE.add(messages=messages_to_add, **params)
        logging.info(f"Memory.add response: {response}")
        if not response.get("results") or len(response.get("results")) == 0:
            error_msg = f"Memory insertion failed: no vectors stored. Response: {response}"
            logging.error(error_msg)
            raise Exception(error_msg)
        return JSONResponse(content=response)
    except Exception as e:
        logging.exception("Error in add_memory:")  # This will log the full traceback
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories", summary="Get memories")
def get_all_memories(
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    agent_id: Optional[str] = None,
):
    """Retrieve stored memories."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    if not any([user_id, run_id, agent_id]):
        raise HTTPException(status_code=400, detail="At least one identifier is required.")
    try:
        params = {k: v for k, v in {"user_id": user_id, "run_id": run_id, "agent_id": agent_id}.items() if v is not None}
        return MEMORY_INSTANCE.get_all(**params)
    except Exception as e:
        logging.exception("Error in get_all_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories/{memory_id}", summary="Get a memory")
def get_memory(memory_id: str):
    """Retrieve a specific memory by ID."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    try:
        return MEMORY_INSTANCE.get(memory_id)
    except Exception as e:
        logging.exception("Error in get_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", summary="Search memories")
def search_memories(search_req: SearchRequest):
    """Search for memories based on a query."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    try:
        params = {k: v for k, v in search_req.model_dump().items() if v is not None and k != "query"}
        return MEMORY_INSTANCE.search(query=search_req.query, **params)
    except Exception as e:
        logging.exception("Error in search_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/memories/{memory_id}", summary="Update a memory")
def update_memory(memory_id: str, updated_memory: Dict[str, Any]):
    """Update an existing memory."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    try:
        if "memory" in updated_memory:
            data = updated_memory["memory"]
        elif "data" in updated_memory:
            data = updated_memory["data"]
        elif "content" in updated_memory:
            data = updated_memory["content"]
        else:
            data = str(updated_memory)
            
        return MEMORY_INSTANCE.update(memory_id=memory_id, data=data)
    except Exception as e:
        logging.exception("Error in update_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories/{memory_id}/history", summary="Get memory history")
def memory_history(memory_id: str):
    """Retrieve memory history."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    try:
        return MEMORY_INSTANCE.history(memory_id=memory_id)
    except Exception as e:
        logging.exception("Error in memory_history:")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memories/{memory_id}", summary="Delete a memory")
def delete_memory(memory_id: str):
    """Delete a specific memory by ID."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    try:
        MEMORY_INSTANCE.delete(memory_id=memory_id)
        return {"message": "Memory deleted successfully"}
    except Exception as e:
        logging.exception("Error in delete_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memories", summary="Delete all memories")
def delete_all_memories(
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    agent_id: Optional[str] = None,
):
    """Delete all memories for a given identifier."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    if not any([user_id, run_id, agent_id]):
        raise HTTPException(status_code=400, detail="At least one identifier is required.")
    try:
        params = {k: v for k, v in {"user_id": user_id, "run_id": run_id, "agent_id": agent_id}.items() if v is not None}
        MEMORY_INSTANCE.delete_all(**params)
        return {"message": "All relevant memories deleted"}
    except Exception as e:
        logging.exception("Error in delete_all_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset", summary="Reset all memories")
def reset_memory():
    """Completely reset stored memories."""
    if not MEMORY_INSTANCE:
        raise HTTPException(status_code=500, detail="Memory instance not initialized")
        
    try:
        MEMORY_INSTANCE.reset()
        return {"message": "All memories reset"}
    except Exception as e:
        logging.exception("Error in reset_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", summary="Health check")
def health_check():
    """Check if the API server is healthy."""
    try:
         if not MEMORY_INSTANCE:
              return JSONResponse(content={"status": "warning", "message": "Memory instance not initialized"}, status_code=200)
         return {"status": "ok"}
    except Exception as e:
         logging.exception("Error in health_check:")
         raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug", summary="Debug server configuration")
def debug_info():
    """Get detailed debug information about the server configuration."""
    config_info = {
        "memory_instance": bool(MEMORY_INSTANCE),
        "vector_store": {
            "provider": DEFAULT_CONFIG["vector_store"]["provider"],
            "host": DEFAULT_CONFIG["vector_store"]["config"]["host"],
            "port": DEFAULT_CONFIG["vector_store"]["config"]["port"],
            "collection_name": DEFAULT_CONFIG["vector_store"]["config"]["collection_name"],
        },
        "graph_store": {
            "provider": DEFAULT_CONFIG["graph_store"]["provider"],
            "url": DEFAULT_CONFIG["graph_store"]["config"]["url"],
        },
        "embedder": {
            "provider": DEFAULT_CONFIG["embedder"]["provider"],
            "model": DEFAULT_CONFIG["embedder"]["config"]["model"],
        },
        "llm": {
            "provider": DEFAULT_CONFIG["llm"]["provider"],
            "model": DEFAULT_CONFIG["llm"]["config"]["model"],
        },
        "api_version": DEFAULT_CONFIG["version"],
        "history_db_path": DEFAULT_CONFIG["history_db_path"],
    }
    
    # Check connections
    connection_status = {}
    
    # Check vector store connection
    try:
        if MEMORY_INSTANCE:
            # Get vector store type
            vector_store_type = type(MEMORY_INSTANCE.vector_store).__name__
            connection_status["vector_store"] = {
                "connected": True,
                "type": vector_store_type,
            }
            
            # Try to list collections
            if hasattr(MEMORY_INSTANCE.vector_store, "list_cols"):
                collections_result = MEMORY_INSTANCE.vector_store.list_cols()
                logging.info(f"Raw list_cols result: {collections_result}") # Add logging

                actual_collections_list = []
                # Check if the result is the expected CollectionsResponse object
                if hasattr(collections_result, 'collections') and isinstance(getattr(collections_result, 'collections'), list):
                    actual_collections_list = collections_result.collections
                    logging.info("Successfully extracted list from CollectionsResponse object.")
                # Fallback for other potential structures (less likely now but kept for safety)
                elif isinstance(collections_result, tuple) and len(collections_result) > 0:
                     potential_list = collections_result[-1]
                     if isinstance(potential_list, list):
                         actual_collections_list = potential_list
                         logging.info("Extracted list from tuple structure.")
                     else:
                         logging.warning(f"Unexpected tuple structure from list_cols: {collections_result}")
                elif isinstance(collections_result, list):
                    actual_collections_list = collections_result
                    logging.info("list_cols returned a direct list.")
                else:
                    logging.warning(f"Unexpected return type or structure from list_cols: {type(collections_result)}, value: {collections_result}")

                # Extract names from CollectionDescription objects in the final list
                collection_names = []
                for item in actual_collections_list:
                    if hasattr(item, "name"):
                        collection_names.append(item.name)
                    else:
                        # Fallback if it's not a CollectionDescription object, maybe it's already a string?
                        collection_names.append(str(item))
                        logging.warning(f"Item in collection list is not a CollectionDescription object: {item}")

                connection_status["vector_store"]["collections"] = collection_names
                logging.info(f"Parsed collection names: {collection_names}") # Add logging

                # Extended Qdrant diagnostics (should now iterate over correct names)
                if vector_store_type in ["Qdrant", "QdrantDB"]:
                    try:
                        connection_status["vector_store"]["collection_details"] = {}
                        for coll_name in connection_status["vector_store"]["collections"]:
                            try:
                                # For Qdrant, get_collection returns a dict with collection info.
                                # get_collection returns a CollectionInfo object, not a dict
                                collection_info: CollectionInfo = MEMORY_INSTANCE.vector_store.client.get_collection(collection_name=coll_name)
                                # Access attributes directly
                                vectors_count = getattr(collection_info, 'vectors_count', 'Unknown')
                                points_count = getattr(collection_info, 'points_count', 'Unknown')
                                status = getattr(collection_info, 'status', 'Unknown') # Assuming status attribute exists

                                connection_status["vector_store"]["collection_details"][coll_name] = {
                                    "vectors_count": vectors_count,
                                    "points_count": points_count,
                                    "status": str(status), # Convert status enum to string if necessary
                                    "exists": True
                                }
                                if hasattr(MEMORY_INSTANCE.vector_store, "collection"):
                                    active_collection = MEMORY_INSTANCE.vector_store.collection
                                    if hasattr(active_collection, "name"):
                                        connection_status["vector_store"]["active_collection"] = active_collection.name
                                    else:
                                        connection_status["vector_store"]["active_collection"] = str(active_collection)
                            except Exception as e:
                                connection_status["vector_store"]["collection_details"][coll_name] = {
                                    "exists": False,
                                    "error": str(e)
                                }
                    except Exception as e:
                        connection_status["vector_store"]["collection_error"] = str(e)
    except Exception as e:
        connection_status["vector_store"] = {
            "connected": False,
            "error": str(e)
        }
    
    # Check graph store connection
    try:
        if MEMORY_INSTANCE and MEMORY_INSTANCE.enable_graph:
            connection_status["graph_store"] = {
                "connected": True,
                "enabled": True
            }
    except Exception as e:
        connection_status["graph_store"] = {
            "connected": False,
            "error": str(e)
        }
    
    # Get user counts and direct memory access
    user_stats = {}
    try:
        # Try to get memory count for a test user
        if MEMORY_INSTANCE:
            test_user = "debug_user"
            memories = MEMORY_INSTANCE.get_all(user_id=test_user)
            user_stats = {
                "test_user_memories": len(memories.get("results", [])) if isinstance(memories, dict) else 0,
                "graph_relationships": len(memories.get("relations", [])) if isinstance(memories, dict) else 0
            }
            
            # Get active users with data (for any vector store)
            try:
                # Add a test memory for diagnosis
                test_content = f"Debug test memory created at {datetime.datetime.now()}"
                test_messages = [{"role": "user", "content": test_content}]
                test_add_result = MEMORY_INSTANCE.add(messages=test_messages, user_id=test_user)
                user_stats["test_add_result"] = test_add_result
                
                # Try direct query
                test_query = "Debug test memory"
                search_result = MEMORY_INSTANCE.search(query=test_query, user_id=test_user)
                user_stats["direct_search_result"] = search_result
            except Exception as e:
                user_stats["test_memory_error"] = str(e)
    except Exception as e:
        user_stats["error"] = str(e)
    
    # Check Memory instance internals
    mem_internals = {}
    try:
        if MEMORY_INSTANCE:
            mem_internals["class"] = type(MEMORY_INSTANCE).__name__
            mem_internals["vector_db_class"] = type(MEMORY_INSTANCE.vector_store).__name__
            mem_internals["enable_graph"] = MEMORY_INSTANCE.enable_graph
            mem_internals["enable_history"] = MEMORY_INSTANCE.enable_history if hasattr(MEMORY_INSTANCE, "enable_history") else False
            
            # Check where mem0 looks for collections
            if hasattr(MEMORY_INSTANCE.vector_store, "collection_name"):
                mem_internals["vector_collection_name"] = MEMORY_INSTANCE.vector_store.collection_name
    except Exception as e:
        mem_internals["error"] = str(e)
        
    return {
        "config": config_info,
        "connections": connection_status,
        "stats": user_stats,
        "memory_internals": mem_internals
    }


@app.get("/", summary="Redirect to the OpenAPI documentation", include_in_schema=False)
def home():
    """Redirect to the OpenAPI documentation."""
    try:
        return RedirectResponse(url='/docs')
    except Exception as e:
        logging.exception("Error in home redirect:")
        raise HTTPException(status_code=500, detail=str(e))