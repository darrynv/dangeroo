import requests
import json

def get_collection_info(collection_name, host="localhost", port=6333):
    """
    Get detailed information about a Qdrant collection
    """
    url = f"http://{host}:{port}/collections/{collection_name}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Format the response JSON for better readability
        collection_info = response.json()
        print(f"Collection Info for '{collection_name}':")
        print(json.dumps(collection_info, indent=2))
        
        # Print some key information
        if 'result' in collection_info:
            result = collection_info['result']
            print("\nKey Collection Info:")
            print(f"- Status: {result.get('status', 'Unknown')}")
            print(f"- Vectors count: {result.get('vectors_count', 'Unknown')}")
            print(f"- Points count: {result.get('points_count', 'Unknown')}")
            print(f"- Segments count: {result.get('segments_count', 'Unknown')}")
            
            # Vector configuration
            if 'config' in result and 'vectors' in result['config']:
                vectors_config = result['config']['vectors']
                if isinstance(vectors_config, dict):
                    for name, config in vectors_config.items():
                        print(f"\nVector '{name}' configuration:")
                        print(f"- Size: {config.get('size', 'Unknown')}")
                        print(f"- Distance: {config.get('distance', 'Unknown')}")
                        print(f"- On-disk: {config.get('on_disk', 'Unknown')}")
                else:
                    print("\nVector configuration:")
                    print(f"- Size: {vectors_config.get('size', 'Unknown')}")
                    print(f"- Distance: {vectors_config.get('distance', 'Unknown')}")
                    print(f"- On-disk: {vectors_config.get('on_disk', 'Unknown')}")
        
        return collection_info
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Error: Collection '{collection_name}' not found!")
        else:
            print(f"HTTP Error: {e}")
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to Qdrant at {host}:{port}")
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def list_collections(host="localhost", port=6333):
    """
    List all available collections in Qdrant
    """
    url = f"http://{host}:{port}/collections"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        collections = response.json().get('result', {}).get('collections', [])
        print("Available Collections:")
        for idx, collection in enumerate(collections, 1):
            print(f"{idx}. {collection.get('name')}")
        
        return collections
    except Exception as e:
        print(f"Error listing collections: {e}")
        return []

if __name__ == "__main__":
    # First list all available collections
    print("Listing all collections in Qdrant:")
    list_collections()
    
    print("\n" + "-"*50 + "\n")
    
    # Then get detailed info for the "memories" collection
    collection_name = "memories"
    get_collection_info(collection_name)