# Dangeroo Mem0 MCP Server

A Model Context Protocol (MCP) server that integrates with [Mem0.ai](https://mem0.ai/) to provide persistent memory capabilities for LLMs. It allows AI agents to store and retrieve information across sessions.

This server extends the functionality of the original Mem0 MCP implementation by adding support for local API endpoints.

## Features

### Storage Modes
* **Cloud Mode** - Connect to Mem0's cloud service using your Mem0 API key
* **Local API Mode** - Connect to a self-hosted Mem0 API instance
* **In-Memory Mode** - Use local vector storage with OpenAI embeddings (non-persistent)

### Tools
* **`add_memory`**: Stores text content as a memory associated with a user
* **`search_memory`**: Searches stored memories using natural language
* **`delete_memory`**: Removes specific memories by ID

## Configuration

This server supports three storage modes controlled by the `MEM0_MODE` environment variable:

1. **Cloud Mode** (`MEM0_MODE=cloud`)
   * Requires `MEM0_API_KEY` environment variable
   * Connects to Mem0's official cloud API

2. **Local API Mode** (`MEM0_MODE=local`)
   * Requires `MEM0_API_ENDPOINT` environment variable (e.g., "http://localhost:8888")
   * Connects to your self-hosted Mem0 API instance
   * No API key required for local instances

3. **In-Memory Mode** (`MEM0_MODE=memory`)
   * Requires `OPENAI_API_KEY` environment variable for embeddings
   * Stores data in-memory only (non-persistent)
   * Data is lost on server restart

### Other Configuration Variables

* `DEFAULT_USER_ID` - Default user identifier to use when none is provided
* `SESSION_ID` - Optional session identifier for grouping memories

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/dangeroo-mem0-mcp.git
cd dangeroo-mem0-mcp

# Install dependencies
npm install

# Build the project
npm run build
```

## MCP Configuration Example

```json
{
  "mcpServers": {
    "mem0": {
      "command": "node",
      "args": [
        "/path/to/dangeroo-mem0-mcp/build/index.js"
      ],
      "env": {
        "MEM0_MODE": "local",
        "MEM0_API_ENDPOINT": "http://localhost:8888",
        "DEFAULT_USER_ID": "user123"
      },
      "disabled": false,
      "alwaysAllow": [
        "add_memory",
        "search_memory",
        "delete_memory"
      ]
    }
  }
}
```

## Usage with Cursor, Claude Code, or other MCP-compatible tools

1. Set up your MCP configuration file to point to this server
2. Configure the appropriate environment variables for your chosen storage mode
3. Use the tools in your LLM interface to store and retrieve memories

## Development

```bash
# Watch for changes during development
npm run watch

# Debug MCP protocol messages
npm run inspector
```