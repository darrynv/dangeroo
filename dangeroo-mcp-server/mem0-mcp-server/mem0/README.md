# Mem0 Memory Tool

A Model Context Protocol (MCP) server that provides memory storage and retrieval capabilities using [Mem0](https://github.com/mem0ai/mem0). This tool allows you to store and search through memories, making it useful for maintaining context and making informed decisions based on past interactions.

## Features

- Store memories with user-specific context
- Search through stored memories with relevance scoring
- Simple and intuitive API
- Built on the Model Context Protocol

## Prerequisites

- Node.js (v14 or higher)
- A Mem0 API key [(Get Here)](https://app.mem0.ai/dashboard/api-keys)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory and add your Mem0 API key:
```bash
MEM0_API_KEY=your-api-key-here
```

## Usage

The server provides two main tools:

### 1. Adding Memories

Store new memories with user-specific context:

```typescript
await server.tool("add-memory", {
  content: "User prefers dark mode interface",
  userId: "alice"
});
```

### 2. Searching Memories

Search through stored memories to retrieve relevant information:

```typescript
const results = await server.tool("search-memories", {
  query: "What are the user's interface preferences?",
  userId: "alice"
});
```

The search results will include:
- Memory content
- Relevance score
- Formatted output for easy integration

## Response Format

### Add Memory Response
```json
{
  "content": [
    {
      "type": "text",
      "text": "Memory added successfully"
    }
  ]
}
```

### Search Memory Response
```json
{
  "content": [
    {
      "type": "text",
      "text": "Memory: User prefers dark mode interface\nRelevance: 0.95\n---"
    }
  ]
}
```

## Development

To run the server in development mode:

```bash
npm run dev
```

## Building

To build the project:

```bash
npm run build
```

## Environment Variables

- `MEM0_API_KEY`: Your Mem0 API key (required)

## License

MIT 