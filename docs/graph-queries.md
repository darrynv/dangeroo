# Example Cypher Queries for Dangeroo Mem0 Neo4j Graph

This document provides example Cypher queries to explore the knowledge graph created by the Mem0 library within the Dangeroo project's Neo4j database.

**Note:** These queries are based on an *assumed* graph schema that Mem0 might create. The actual labels, relationship types, and property names might differ slightly. It's recommended to inspect your actual graph data using Neo4j Browser (`http://localhost:7474`) and queries like `CALL db.schema.visualization()` to confirm the schema before running complex queries.

## Assumed Schema Overview

*   **Nodes:** `Memory`, `Entity`, `Concept`, `User`, `Agent`, `Run`
*   **Relationships:** `CONTAINS_ENTITY`, `MENTIONS_CONCEPT`, `RELATED_TO`, `CREATED_BY_USER`, `CREATED_BY_AGENT`, `PART_OF_RUN`
*   **Key Properties:**
    *   `Memory`: `memory_id`, `user_id`, `agent_id`, `run_id`
    *   `Entity`: `name`, `type`
    *   `Concept`: `name`, `type` (e.g., type='language', name='Python'; type='topic', name='API Integration')
    *   `User`: `user_id`
    *   `Agent`: `agent_id`
    *   `Run`: `run_id`

---

## Example Queries

### 1. Basic Relationship Queries

**a) Find all memories created by a specific user:**

```cypher
MATCH (u:User {user_id: 'python_dev_01'})<-[:CREATED_BY_USER]-(m:Memory)
RETURN m.memory_id, m.user_id
LIMIT 25;
```
*Explanation:* Finds the `User` node with `user_id` 'python_dev_01', then follows incoming `CREATED_BY_USER` relationships to find connected `Memory` nodes.

**b) Find all entities mentioned within a specific memory (by run_id):**
*(Requires knowing the specific memory_id, which isn't directly in the input script. Using run_id as a proxy)*

```cypher
MATCH (run:Run {run_id: 'python_session_lc_20250424_01'})<-[:PART_OF_RUN]-(m:Memory)-[:CONTAINS_ENTITY]->(e:Entity)
RETURN m.memory_id, e.name, e.type
LIMIT 50;
```
*Explanation:* Finds the `Run` node, gets the associated `Memory`, and then finds all `Entity` nodes connected via the `CONTAINS_ENTITY` relationship.

**c) Find all concepts associated with a specific memory (by run_id):**

```cypher
MATCH (run:Run {run_id: 'python_session_lc_20250424_01'})<-[:PART_OF_RUN]-(m:Memory)-[:MENTIONS_CONCEPT]->(c:Concept)
RETURN m.memory_id, c.type, c.name
LIMIT 50;
```
*Explanation:* Similar to the entity query, but follows the `MENTIONS_CONCEPT` relationship to find linked `Concept` nodes derived from metadata.

### 2. Domain-Specific Queries

**a) Find all memories discussing the Python language:**

```cypher
MATCH (lang:Concept {type: 'language', name: 'Python'})<-[:MENTIONS_CONCEPT]-(m:Memory)
RETURN m.memory_id, m.user_id
LIMIT 25;
```
*Explanation:* Finds the `Concept` node representing the Python language and retrieves all `Memory` nodes linked to it.

**b) Find all memories where the topic is 'API Integration':**

```cypher
MATCH (topic:Concept {type: 'topic', name: 'API Integration'})<-[:MENTIONS_CONCEPT]-(m:Memory)
RETURN m.memory_id, m.user_id
LIMIT 25;
```
*Explanation:* Finds the `Concept` node for the 'API Integration' topic and retrieves associated memories.

**c) Find entities related to 'OpenAI API':**
*(Assumes 'OpenAI API' is extracted as an Entity)*

```cypher
MATCH (e1:Entity {name: 'OpenAI API'})-[r:RELATED_TO]-(e2:Entity)
RETURN e1.name, type(r) AS relationship, e2.name
LIMIT 50;
```
*Explanation:* Finds the 'OpenAI API' `Entity` node and explores outgoing/incoming `RELATED_TO` relationships to find directly connected entities.

### 3. Finding Connections Between Different Domains

**a) Find users who have memories related to both 'Python' and 'OpenAI API':**

```cypher
MATCH (u:User)<-[:CREATED_BY_USER]-(m1:Memory)-[:MENTIONS_CONCEPT]->(c1:Concept {type: 'language', name: 'Python'})
MATCH (u)<-[:CREATED_BY_USER]-(m2:Memory)-[:MENTIONS_CONCEPT]->(c2:Concept {type: 'sub_topic', name: 'OpenAI API'})
RETURN DISTINCT u.user_id;

// Alternative using Entities if 'OpenAI API' is an entity:
MATCH (u:User)<-[:CREATED_BY_USER]-(m1:Memory)-[:MENTIONS_CONCEPT]->(c1:Concept {type: 'language', name: 'Python'})
MATCH (u)<-[:CREATED_BY_USER]-(m2:Memory)-[:CONTAINS_ENTITY]->(e:Entity {name: 'OpenAI API'})
RETURN DISTINCT u.user_id;

```
*Explanation:* Finds users (`u`) connected to memories mentioning the 'Python' concept AND also connected (potentially via different memories) to memories mentioning the 'OpenAI API' concept (or entity). `DISTINCT` ensures each user is listed only once.

**b) Find concepts often mentioned together with 'Semantic Search':**

```cypher
MATCH (ss_concept:Concept {name: 'Semantic Search vs Keyword Search'})<-[:MENTIONS_CONCEPT]-(m:Memory)-[:MENTIONS_CONCEPT]->(other_concept:Concept)
WHERE ss_concept <> other_concept // Avoid matching the concept to itself
RETURN other_concept.type, other_concept.name, COUNT(*) AS frequency
ORDER BY frequency DESC
LIMIT 20;
```
*Explanation:* Finds memories mentioning 'Semantic Search', then finds all *other* concepts mentioned in those *same* memories. It counts the frequency of these co-occurring concepts.

### 4. Knowledge Graph Traversal

**a) Find concepts related to the 'List Comprehensions' entity (multi-step):**
*(Assumes 'List Comprehensions' is an Entity)*

```cypher
MATCH (lc:Entity {name: 'List Comprehensions'})<-[:CONTAINS_ENTITY]-(m:Memory)-[:MENTIONS_CONCEPT]->(c:Concept)
RETURN DISTINCT c.type, c.name;
```
*Explanation:* Finds the 'List Comprehensions' entity, traverses back to the memory containing it, then finds all concepts associated with that memory.

**b) Find entities that are related to entities contained within 'Python' memories:**

```cypher
MATCH (py:Concept {type: 'language', name: 'Python'})<-[:MENTIONS_CONCEPT]-(m:Memory)-[:CONTAINS_ENTITY]->(e1:Entity)
MATCH (e1)-[:RELATED_TO]-(e2:Entity)
WHERE NOT (m)-[:CONTAINS_ENTITY]->(e2) // Optional: Exclude entities also directly in the same memory
RETURN DISTINCT e1.name AS source_entity, e2.name AS related_entity
LIMIT 50;

```
*Explanation:* Finds Python memories, finds entities within them (`e1`), then finds other entities (`e2`) related to `e1` via the `RELATED_TO` relationship.

### 5. Temporal Analysis (Requires Timestamp Property)

**Note:** These queries assume a `timestamp` property exists on `Memory` nodes (e.g., storing creation time). Mem0 might store this; verification is needed.

**a) Find memories created by 'python_dev_01' within a specific date range:**
*(Assuming timestamp is stored as epoch milliseconds or ISO 8601 string)*

```cypher
// Example using epoch milliseconds
MATCH (u:User {user_id: 'python_dev_01'})<-[:CREATED_BY_USER]-(m:Memory)
WHERE m.timestamp >= apoc.date.parse('2025-04-24T00:00:00Z', 'ms', 'yyyy-MM-dd\'T\'HH:mm:ss\'Z\'')
  AND m.timestamp < apoc.date.parse('2025-04-25T00:00:00Z', 'ms', 'yyyy-MM-dd\'T\'HH:mm:ss\'Z\'')
RETURN m.memory_id, datetime({epochMillis: m.timestamp}) AS creation_time
ORDER BY m.timestamp DESC;

// Example using ISO 8601 string timestamp
MATCH (u:User {user_id: 'python_dev_01'})<-[:CREATED_BY_USER]-(m:Memory)
WHERE m.timestamp >= '2025-04-24T00:00:00Z'
  AND m.timestamp < '2025-04-25T00:00:00Z'
RETURN m.memory_id, m.timestamp
ORDER BY m.timestamp DESC;
```
*Explanation:* Finds memories for the user and filters them based on the `timestamp` property falling within the specified range. Requires APOC library for epoch conversion if timestamps are stored as numbers.

**b) Count memories added per day:**
*(Requires timestamp property)*

```cypher
MATCH (m:Memory)
WHERE m.timestamp IS NOT NULL // Ensure timestamp exists
WITH datetime({epochMillis: m.timestamp}) AS dt // Or directly use m.timestamp if string
RETURN date(dt) AS memory_date, COUNT(*) AS memories_added
ORDER BY memory_date DESC
LIMIT 30;
```
*Explanation:* Extracts the date part from the memory timestamp and counts how many memories were created on each date.

---

Remember to adapt these queries based on the actual schema you observe in your Neo4j database.