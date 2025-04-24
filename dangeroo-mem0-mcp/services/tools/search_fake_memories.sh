#!/bin/bash

# Script to demonstrate various search queries against the Mem0 API v2
# using the memories injected by inject_fake_memories.sh

API_SEARCH_URL="http://localhost:8888/search"
DEBUG=true # Set to false to hide curl command and response details
DEFAULT_LIMIT=5
DEFAULT_THRESHOLD=0.4

# Function to print debug messages
debug_log() {
  if [ "$DEBUG" = true ]; then
    echo "[DEBUG] $1"
  fi
}

# Function to execute search and print results
execute_search() {
  local description="$1"
  local payload="$2"
  local temp_file="results_temp.json"

  echo "--- Executing Search: $description ---"
  debug_log "Payload: $payload"

  # Execute curl command
  debug_log "Executing: curl -s -X POST \"${API_SEARCH_URL}\" -H \"Content-Type: application/json\" -d '$payload'"
  curl_output=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${API_SEARCH_URL}" \
    -H "Content-Type: application/json" \
    -d "$payload")

  # Extract status code and response body
  http_status=$(echo "$curl_output" | tail -n1)
  response_body=$(echo "$curl_output" | sed '$d')

  debug_log "Raw Response Body: $response_body"
  debug_log "$http_status"

  echo "$response_body" > "$temp_file"

  # Check HTTP status and process response
  if [[ "$http_status" != "HTTP_STATUS:2"* ]]; then
    echo "[ERROR] Search failed ($http_status)"
    jq . "$temp_file" 2>/dev/null || cat "$temp_file" # Try to pretty-print JSON, otherwise show raw
  elif ! jq . "$temp_file" > /dev/null 2>&1; then
     echo "[ERROR] Invalid JSON response"
     cat "$temp_file"
  else
    echo "[SUCCESS] Search results:"
    # Show count and first result clearly
    jq --argjson limit "$DEFAULT_LIMIT" --argjson threshold "$DEFAULT_THRESHOLD" \
       '.results | length as $len | "\($len) result(s) found (limit=\($limit), threshold=\($threshold)). First result (if any):", (if $len > 0 then .results[0] else "No matching results based on vector similarity." end), ("Graph Relations found:", .relations // [])' \
       "$temp_file"
    # Use this line to see the full results object:
    # jq . "$temp_file"
  fi

  rm -f "$temp_file"
  echo "------------------------------------------"
  echo "" # Add a newline for better readability
  sleep 1 # Pause briefly between requests
}

echo "Starting Mem0 v2 Search Examples (Corrected)..."
echo "API Search URL: $API_SEARCH_URL"
echo "Default Limit: $DEFAULT_LIMIT, Default Threshold: $DEFAULT_THRESHOLD"
echo "=========================================="

# Example 1: Basic text search for a specific concept
execute_search "Basic text search for 'python list comprehension'" \
'{
  "query": "concise list creation python",
  "user_id": "python_dev_01",
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 2: Text search scoped to a specific user
execute_search "Text search for 'OpenAI API' for user 'ai_integrator_02'" \
'{
  "query": "call openai completions endpoint",
  "user_id": "ai_integrator_02",
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 3: Text search scoped to a specific agent (CORRECTED: added user_id)
# Note: Added user_id as it seems required by the backend implementation detail.
execute_search "Text search for 'decorators' handled by agent 'coding_assistant_py'" \
'{
  "query": "what does @ signify in python",
  "user_id": "python_dev_04",
  "agent_id": "coding_assistant_py",
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 4: Metadata filter - Find all Python memories
execute_search "Metadata filter for language: Python" \
'{
  "query": "python code examples",
  "user_id": "python_dev_01",
  "filters": {
    "language": "Python"
  },
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 5: Combined Metadata filter - Python + API Integration (CORRECTED: filter structure)
execute_search "Combined metadata filter: Language=Python AND Topic='API Integration'" \
'{
  "query": "using external APIs in python",
  "user_id": "ai_integrator_05",
  "filters": {
    "AND": [
      {"field": "language", "value": "Python"},
      {"field": "topic", "value": "API Integration"}
    ]
  },
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 6: Filter by specific run_id (CORRECTED: added user_id)
# Note: Added user_id as it seems required by the backend implementation detail.
execute_search "Filter by specific run_id for asyncio example" \
'{
  "query": "asyncio",
  "user_id": "python_dev_07",
  "run_id": "python_asyncio_session_20250424_07",
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 7: Conceptual search - Error handling
execute_search "Conceptual search for Python error handling" \
'{
  "query": "how to handle file not found in python",
  "user_id": "python_dev_10",
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 8: Search by a different user for semantic search concepts
execute_search "Search by 'ai_researcher_03' for semantic search concepts" \
'{
  "query": "difference between keyword and semantic search",
  "user_id": "ai_researcher_03",
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 9: Metadata filter - Find all 'Intermediate' difficulty memories
execute_search "Metadata filter for difficulty: Intermediate" \
'{
  "query": "intermediate concepts",
  "user_id": "python_dev_04",
  "filters": {
    "difficulty": "Intermediate"
  },
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

# Example 10: Metadata filter - Find memories related to OpenAI (using concepts) (CORRECTED: filter structure)
execute_search "Metadata filter using concepts array for 'OpenAI API'" \
'{
  "query": "OpenAI related",
  "user_id": "ai_integrator_02",
  "filters": {
     "field": "concepts",
     "operator": "contains",
     "value": "OpenAI API"
  },
  "limit": '$DEFAULT_LIMIT',
  "threshold": '$DEFAULT_THRESHOLD'
}'

echo "=========================================="
echo "Corrected Search Examples Complete."
echo "Set DEBUG=true in the script to see full request/response details."