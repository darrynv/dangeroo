# Used to check direct memory injection and Qdrant connection
# This script is intended to be run in the same environment as the main.py
import os
import logging
from mem0 import Memory
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file (especially OPENAI_API_KEY)
load_dotenv()

# Configuration for Mem0
# Assumes Qdrant is running in Docker network with service name 'qdrant'
# Uses the default collection name 'memories' from main.py environment setup
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": os.getenv("QDRANT_COLLECTION_NAME", "memories"), # Use env var or default
            "host": os.getenv("QDRANT_HOST", "qdrant"), # Use env var or default 'qdrant' for docker
            "port": int(os.getenv("QDRANT_PORT", 6333)), # Use env var or default
            # Add other Qdrant config if needed, e.g., on_disk, path, api_key
            "on_disk": os.getenv("QDRANT_ONDISK", "False").lower() == "true",
            "path": os.getenv("QDRANT_PATH", None), # Path might be relevant if on_disk=True
        }
    },
     "embedder": { # Add embedder config as it's likely required by Memory class
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            # API key is usually picked up from env automatically by mem0/openai client
        }
    },
    # Add LLM config if graph features or other LLM-dependent parts are implicitly used
    # "llm": {
    #     "provider": "openai",
    #     "config": {
    #         "model": "gpt-4o"
    #     }
    # }
}

logging.info(f"Using Mem0 config: {config}")

try:
    # Initialize Memory instance
    m = Memory.from_config(config)
    logging.info("Memory instance initialized successfully.")

    # --- Memory Examples ---

    # Example 1: Python List Comprehension
    logging.info("Attempting to add Memory Example #1 (Python List Comprehension)")
    messages_1 = [
        {"role": "system", "content": "Python coding assistance session."},
        {"role": "user", "content": "How can I create a list of squares for numbers 0 through 9 in Python concisely?"},
        {"role": "assistant", "content": "Use a list comprehension: `squares = [x**2 for x in range(10)]`."},
        {"role": "user", "content": "Can I add a condition, like only squaring even numbers?"},
        {"role": "assistant", "content": "Yes: `even_squares = [x**2 for x in range(10) if x % 2 == 0]`."}
    ]
    metadata_1 = {
        "language": "Python", "topic": "Core Language Features", "sub_topic": "List Comprehensions",
        "concepts": ["iteration", "list creation", "conditional logic"], "difficulty": "Beginner",
        "task_type": "code_generation_explanation"
    }
    try:
        result_1 = m.add(messages_1, user_id="python_dev_01", metadata=metadata_1)
        logging.info(f"Memory 1 m.add() returned: {result_1}") # Explicitly log return value
        logging.info(f"Memory 1 added successfully.")
    except Exception as e:
        logging.error(f"Error adding Memory 1: {e}", exc_info=True)

    # Example 2: OpenAI API Call (Completions)
    logging.info("Attempting to add Memory Example #2 (OpenAI API Call)")
    messages_2 = [
        {"role": "system", "content": "Assisting with OpenAI API integration in Python."},
        {"role": "user", "content": "How do I set up the client and make a basic chat completion request for gpt-4o?"},
        {"role": "assistant", "content": "Instantiate with `client = OpenAI()` (uses env var) and call `client.chat.completions.create(...)` with model and messages."},
        {"role": "user", "content": "How do I access the response content?"},
        {"role": "assistant", "content": "Usually via `response.choices[0].message.content`."}
    ]
    metadata_2 = {
        "language": "Python", "topic": "API Integration", "sub_topic": "OpenAI API",
        "concepts": ["API client", "authentication", "chat completions", "response parsing"], "difficulty": "Intermediate",
        "task_type": "code_example_usage", "libraries": ["openai"], "external_service": "OpenAI"
    }
    try:
        result_2 = m.add(messages_2, user_id="ai_integrator_02", metadata=metadata_2)
        logging.info(f"Memory 2 added successfully: {result_2}")
    except Exception as e:
        logging.error(f"Error adding Memory 2: {e}", exc_info=True)

    # Example 3: Semantic Search Concept
    logging.info("Attempting to add Memory Example #3 (Semantic Search Concept)")
    messages_3 = [
        {"role": "system", "content": "Explaining core AI and search concepts."},
        {"role": "user", "content": "What's the difference between keyword search and semantic search?"},
        {"role": "assistant", "content": "Keyword search matches exact terms. Semantic search understands meaning and intent using vector embeddings to find conceptually similar results, even without exact keyword matches."},
        {"role": "user", "content": "How are embeddings generated?"},
        {"role": "assistant", "content": "Deep learning models map text to vectors in a high-dimensional space, where similar texts have vectors close to each other."}
    ]
    metadata_3 = {
        "language": "Conceptual", "topic": "Search Technology", "sub_topic": "Semantic Search vs Keyword Search",
        "concepts": ["search algorithms", "vector embeddings", "similarity", "NLP"], "difficulty": "Intermediate",
        "task_type": "concept_explanation", "related_technologies": ["Vector Databases", "OpenAI Embeddings"]
    }
    try:
        result_3 = m.add(messages_3, user_id="ai_researcher_03", metadata=metadata_3)
        logging.info(f"Memory 3 added successfully: {result_3}")
    except Exception as e:
        logging.error(f"Error adding Memory 3: {e}", exc_info=True)

    # Example 4: Python Decorators
    logging.info("Attempting to add Memory Example #4 (Python Decorators)")
    messages_4 = [
        {"role": "system", "content": "Explaining advanced Python features."},
        {"role": "user", "content": "What does the `@some_name` syntax mean above Python functions?"},
        {"role": "assistant", "content": "That's a decorator. It's syntactic sugar to modify or enhance a function, often used for logging, timing, or access control."},
        {"role": "user", "content": "Can you show a simple timing example?"},
        {"role": "assistant", "content": "Yes, you define a wrapper function that records time before and after calling the original function, then apply it with `@timer`."}
    ]
    metadata_4 = {
        "language": "Python", "topic": "Advanced Language Features", "sub_topic": "Decorators",
        "concepts": ["metaprogramming", "higher-order functions", "closures", "syntactic sugar"], "difficulty": "Intermediate",
        "task_type": "concept_explanation_code_example"
    }
    try:
        result_4 = m.add(messages_4, user_id="python_dev_04", metadata=metadata_4)
        logging.info(f"Memory 4 added successfully: {result_4}")
    except Exception as e:
        logging.error(f"Error adding Memory 4: {e}", exc_info=True)

    # Example 5: Python Error Handling (Try/Except)
    logging.info("Attempting to add Memory Example #5 (Python Error Handling)")
    messages_5 = [
        {"role": "system", "content": "Python error handling best practices."},
        {"role": "user", "content": "How do I prevent my script from crashing if a file doesn't exist?"},
        {"role": "assistant", "content": "Use a `try...except FileNotFoundError:` block. Put the file opening code in `try`, and the handling code (e.g., print message) in `except`."},
    ]
    metadata_5 = {
        "language": "Python", "topic": "Core Language Features", "sub_topic": "Error Handling",
        "concepts": ["exceptions", "try/except", "FileNotFoundError", "graceful failure"], "difficulty": "Beginner",
        "task_type": "code_example_best_practice"
    }
    try:
        result_5 = m.add(messages_5, user_id="python_dev_10", metadata=metadata_5)
        logging.info(f"Memory 5 added successfully: {result_5}")
    except Exception as e:
        logging.error(f"Error adding Memory 5: {e}", exc_info=True)

    logging.info("Debug script finished.")

except Exception as e:
    logging.error(f"Failed to initialize Memory instance or run script: {e}", exc_info=True)