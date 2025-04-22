#!/usr/bin/env python3

"""
Diagnostic script to debug Mem0 API initialization
python3 -m venv mem0_env
source mem0_env/bin/activate
pip install mem0ai python-dotenv chromadb openai neo4j langchain-neo4j rank-bm25

- Can also use this to check if the chromadb server is running 
python3 -c "import chromadb; client = chromadb.HttpClient(host='localhost', port=8000); print(f'Connected to ChromaDB, heartbeat: {client.heartbeat()}')"

- And this for neo4j
python3 -c "
from neo4j import GraphDatabase;
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'mem0graph'));
with driver.session() as session:
    result = session.run('RETURN 1 AS num');
    print(f'Connected to Neo4j, result: {result.single()[\"num\"]}');
driver.close()
"
"""



import sys
import logging
import os
import uuid
from mem0 import Memory
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# External connection details (from host machine to Docker containers)
CHROMA_HOST = "localhost"  # External hostname for ChromaDB
CHROMA_PORT = 8000         # External port for ChromaDB
NEO4J_URI = "bolt://localhost:7687"  # External URI for Neo4j
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "mem0graph")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
HISTORY_DB_PATH = "./debug_history.db"  # Local file in current directory

def main():
    """Test mem0 configuration and initialization"""
    logger.info("Starting Mem0 diagnostic test with fixed external connection details")
    
    # Display configuration
    logger.info("Configuration:")
    logger.info(f"CHROMA_HOST: {CHROMA_HOST}")
    logger.info(f"CHROMA_PORT: {CHROMA_PORT}")
    logger.info(f"NEO4J_URI: {NEO4J_URI}")
    logger.info(f"NEO4J_USERNAME: {NEO4J_USERNAME}")
    logger.info(f"HISTORY_DB_PATH: {HISTORY_DB_PATH}")
    logger.info(f"OPENAI_API_KEY: {'Set' if OPENAI_API_KEY else 'Not set'}")
    
    try:
        # Create configuration
        config = {
            "version": "v1.1",
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "host": CHROMA_HOST,
                    "port": CHROMA_PORT,
                    "collection_name": "test_collection"
                }
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
                    "model": "text-embedding-3-small"
                }
            },
            "history_db_path": HISTORY_DB_PATH,
        }
        
        logger.info("Initializing Memory instance...")
        memory = Memory.from_config(config)
        logger.info("Memory instance initialized successfully")
        
        # Test basic functionality
        logger.info("Testing memory operations...")
        
        # Generate a unique user ID for testing
        user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        logger.info(f"Using test user ID: {user_id}")
        
        # Add a test memory
        test_message = "This is a test memory from the diagnostic script."
        messages = [{"role": "user", "content": test_message}]
        
        logger.info("Adding test memory...")
        add_result = memory.add(messages=messages, user_id=user_id)
        logger.info(f"Memory added successfully: {add_result}")
        
        # Search for the memory
        logger.info("Searching for test memory...")
        search_results = memory.search(query="test memory", user_id=user_id)
        logger.info(f"Search results: {search_results}")
        
        logger.info("All tests completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error in Mem0 diagnostic: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())