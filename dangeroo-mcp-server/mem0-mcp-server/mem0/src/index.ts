import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { MemoryClient } from 'mem0ai';

const MEM0_API_KEY = process?.env?.MEM0_API_KEY || '';

// Initialize mem0ai client
const memoryClient = new MemoryClient({ apiKey: MEM0_API_KEY });

// Create server instance
const server = new McpServer({
  name: "mem0",
  version: "1.0.0",
  capabilities: {
    resources: {},
    tools: {},
  },
});

// Helper function to add memories
async function addMemory(content: string, userId: string) {
  try {
    const messages = [
      { role: "system", content: "Memory storage system" },
      { role: "user", content }
    ];
    await memoryClient.add(messages, { user_id: userId });
  } catch (error) {
    console.error("Error adding memory:", error);
  }
}

// Helper function to search memories
async function searchMemories(query: string, userId: string) {
  try {
    const results = await memoryClient.search(query, { user_id: userId });
    return results;
  } catch (error) {
    console.error("Error searching memories:", error);
    return [];
  }
}

// Register memory tools
server.tool(
  "add-memory",
  "Add a new memory. This method is called everytime the user informs anything about themselves, their preferences, or anything that has any relevent information whcih can be useful in the future conversation. This can also be called when the user asks you to remember something.",
  {
    content: z.string().describe("The content to store in memory"),
    userId: z.string().describe("User ID for memory storage. If not provided explicitly, use a generic user ID like, 'mem0-mcp-user'"),
  },
  async ({ content, userId }) => {
    await addMemory(content, userId);
    return {
      content: [
        {
          type: "text",
          text: "Memory added successfully",
        },
      ],
    };
  },
);

server.tool(
  "search-memories",
  "Search through stored memories. This method is called ANYTIME the user asks anything.",
  {
    query: z.string().describe("The search query. This is the query that the user has asked for. Example: 'What did I tell you about the weather last week?' or 'What did I tell you about my friend John?'"),
    userId: z.string().describe("User ID for memory storage. If not provided explicitly, use a generic user ID like, 'mem0-mcp-user"),
  },
  async ({ query, userId }) => {
    const results = await searchMemories(query, userId);
    const formattedResults = results.map((result: any) => 
      `Memory: ${result.memory}\nRelevance: ${result.score}\n---`
    ).join("\n");

    return {
      content: [
        {
          type: "text",
          text: formattedResults || "No memories found",
        },
      ],
    };
  },
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Memory MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});