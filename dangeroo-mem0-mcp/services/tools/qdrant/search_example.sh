# SEMANTIC/CONCEPTUAL SEARCHES
# Conceptual search about network problems (should find the router firmware issue)
curl -X POST "http://localhost:8888/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "why does my internet keep disconnecting?",
    "user_id": "tech_support_customer_404"
  }' > results.json
jq . results.json

# Semantic search for retirement planning
curl -X POST "http://localhost:8888/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how should I invest for retirement with moderate risk?",
    "user_id": "financial_client_303"
  }' > results.json
jq . results.json


# Semantic search for retirement planning
curl -X POST "http://localhost:8888/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python module not found error",
  "userId": "rooCode_mcp",
  "filters": {
    "AND": [
      {"type": "bug_analysis"},
      {"category": "module_reference_error"},
      {"language": "python"},
      {"source": "manual_test_entry"}
    ]
  },
  "threshold": 0.7
  }' > results.json
jq . results.json


# Conceptual search for language learning difficulties
curl -X POST "http://localhost:8888/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "struggling with Spanish past tense verbs",
    "user_id": "language_learner_789"
  }' > results.json
jq . results.json


# CROSS TOPICAL SEARCHES
# Search for all fitness-related memories
curl -X POST "http://localhost:8888/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "exercise workout fitness training"
  }' > results.json
jq . results.json

# Search for all food-related memories
curl -X POST "http://localhost:8888/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cooking recipes food dishes"
  }' > results.json
jq . results.json

# Search for all educational content
curl -X POST "http://localhost:8888/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "learning education teaching student progress"
  }' > results.json
jq . results.json