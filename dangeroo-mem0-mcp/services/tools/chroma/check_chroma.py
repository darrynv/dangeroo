#pip install chromadb
import chromadb
import os

# Define the ChromaDB server endpoint
CHROMA_HOST = os.environ.get("CHROMA_HOST_TOOL", "localhost") # Use localhost if running script from host
CHROMA_PORT = int(os.environ.get("CHROMA_PORT_TOOL", 8000))

print(f"Attempting to connect to ChromaDB server at: http://{CHROMA_HOST}:{CHROMA_PORT}")

try:
    # Initialize the HTTP client
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    # Verify connection by getting heartbeat
    client.heartbeat()
    print("Successfully connected to ChromaDB server.")

    # List all collections
    collections = client.list_collections()

    print("\nChromaDB Collections Found:")
    if collections:
        for collection in collections:
            print(f"- {collection.name}")
            # Optionally, get item count:
            # try:
            #     count = collection.count()
            #     print(f"  Item count: {count}")
            # except Exception as e:
            #     print(f"  Could not get count for collection {collection.name}: {e}")
    else:
        print("No collections found.")

except Exception as e:
    print(f"\nError connecting to or querying ChromaDB server: {e}")
    print("Please ensure:")
    print("1. The ChromaDB Docker container ('chroma') is running (`docker-compose ps` in the 'services' directory).")
    print(f"2. The server is accessible at http://{CHROMA_HOST}:{CHROMA_PORT} from where you are running this script.")
    print("3. The 'chromadb' Python package is installed in your environment (`pip install chromadb`).")