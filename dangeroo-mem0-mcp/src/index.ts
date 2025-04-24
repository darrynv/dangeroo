#!/usr/bin/env node

/**
 * MCP server for interacting with dgroo-fast-api or local in-memory storage.
 * Provides tools to add, search, and delete memories.
 *
 * Supports two modes:
 * 1. Local API mode: Uses the self-hosted dgroo-fast-api endpoint (DGROO_FAST_API_ENDPOINT)
 * 2. Memory mode: Uses in-memory storage with OPENAI_API_KEY for embeddings
 */

// Load environment variables from .env file if present
import { config as loadDotEnv } from 'dotenv';
loadDotEnv();

// Create a wrapper around console to safely redirect logs from libraries
// This ensures MCP protocol communication is not affected
class SafeLogger {
  private originalConsoleLog: typeof console.log;
  
  constructor() {
    // Store the original console.log
    this.originalConsoleLog = console.log;
    
    // Redirect console.log to stderr only for our module
    console.log = (...args) => {
      // Check if it's from the mem0ai library or our code
      const stack = new Error().stack || '';
      if (stack.includes('mem0ai') || stack.includes('mem0-mcp')) {
        console.error('[redirected log]', ...args);
      } else {
        // Keep normal behavior for MCP protocol and other code
        this.originalConsoleLog.apply(console, args);
      }
    };
  }
  
  // Restore original behavior
  restore() {
    console.log = this.originalConsoleLog;
  }
}

// Apply the safe logger
const safeLogger = new SafeLogger();

// Disable debug logs in any libraries that respect these environment variables
process.env.DEBUG = '';  // Disable debug logs
process.env.NODE_DEBUG = ''; // Disable Node.js internal debugging
process.env.DEBUG_COLORS = 'no'; // Disable color output in logs
process.env.NODE_ENV = process.env.NODE_ENV || 'production'; // Use production mode by default
process.env.LOG_LEVEL = 'error'; // Set log level to error only
process.env.SILENT = 'true'; // Some libraries respect this
process.env.QUIET = 'true'; // Some libraries respect this

// IMPORTANT: Don't globally override stdout as it breaks MCP protocol
// We'll use more targeted approaches in specific methods

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  McpError,
  ErrorCode,
} from "@modelcontextprotocol/sdk/types.js";

import { Memory } from "mem0ai/oss"; // For local in-memory storage
import axios from 'axios'; // For HTTP requests to local API endpoint

// Cloud client removed as it's deprecated

// Storage mode types
enum StorageMode {
  LOCAL_API = 'local',
  IN_MEMORY = 'memory'
}

// Type for the arguments received by the MCP tool handlers
type Mem0AddToolArgs = {
  content: string;
  userId: string;
  sessionId?: string;
  agentId?: string;
  metadata?: Record<string, any>;
};

type Mem0SearchToolArgs = {
  query: string;
  userId: string;
  sessionId?: string;
  agentId?: string;
  filters?: Record<string, any>;
  threshold?: number;
};

type Mem0DeleteToolArgs = {
  memoryId: string;
  userId: string;
  sessionId?: string;
  agentId?: string;
};

// Message type for Mem0 API
type Mem0Message = {
  role: "user" | "assistant" | "system";
  content: string;
};

// Local API interface for the REST endpoint
class LocalApiClient {
  private baseUrl: string;
  
  constructor(apiEndpoint: string) {
    // Ensure the endpoint doesn't end with a slash
    this.baseUrl = apiEndpoint.endsWith('/') 
      ? apiEndpoint.slice(0, -1) 
      : apiEndpoint;
      
    console.error(`Initialized Local API client with endpoint: ${this.baseUrl}`);
  }
  
  async add(messages: Mem0Message[], options: any = {}): Promise<any> {
    try {
      const payload = {
        messages,
        user_id: options.userId || options.user_id,
        run_id: options.sessionId || options.run_id,
        agent_id: options.agentId || options.agent_id,
        metadata: options.metadata
      };
      
      const response = await axios.post(`${this.baseUrl}/memories`, payload);
      return response.data;
    } catch (error: any) {
      console.error("Error in Local API add:", error.message);
      if (error.response) {
        console.error("Response data:", error.response.data);
      }
      throw error;
    }
  }
  
  async search(query: string, options: any = {}): Promise<any> {
    try {
      const payload = {
        query,
        user_id: options.userId || options.user_id,
        run_id: options.sessionId || options.run_id,
        agent_id: options.agentId || options.agent_id,
        filters: options.filters
      };
      
      const response = await axios.post(`${this.baseUrl}/search`, payload);
      return response.data;
    } catch (error: any) {
      console.error("Error in Local API search:", error.message);
      if (error.response) {
        console.error("Response data:", error.response.data);
      }
      throw error;
    }
  }
  
  async delete(memoryId: string, options: any = {}): Promise<any> {
    try {
      // Local API uses direct endpoint for memory deletion
      const response = await axios.delete(`${this.baseUrl}/memories/${memoryId}`);
      return response.data;
    } catch (error: any) {
      console.error("Error in Local API delete:", error.message);
      if (error.response) {
        console.error("Response data:", error.response.data);
      }
      throw error;
    }
  }
  
  async getAll(options: any = {}): Promise<any> {
    try {
      // Build query parameters for filtering
      const params = new URLSearchParams();
      if (options.userId || options.user_id) {
        params.append('user_id', options.userId || options.user_id);
      }
      if (options.sessionId || options.run_id) {
        params.append('run_id', options.sessionId || options.run_id);
      }
      if (options.agentId || options.agent_id) {
        params.append('agent_id', options.agentId || options.agent_id);
      }
      
      const url = `${this.baseUrl}/memories?${params.toString()}`;
      const response = await axios.get(url);
      return response.data;
    } catch (error: any) {
      console.error("Error in Local API getAll:", error.message);
      if (error.response) {
        console.error("Response data:", error.response.data);
      }
      throw error;
    }
  }
}

class Mem0MCPServer {
  private server: Server;
  private storageMode: StorageMode;
  private localClient?: Memory;           // In-memory storage client
  private localApiClient?: LocalApiClient; // dgroo-fast-api REST API client
  private isReady: boolean = false;

  constructor() {
    console.error("Initializing Dangeroo Mem0 MCP Server...");
    
    // Determine storage mode based on environment variables
    const dgrooApiEndpoint = process.env.DGROO_FAST_API_ENDPOINT;
    const openaiApiKey = process.env.OPENAI_API_KEY;

    if (dgrooApiEndpoint) {
      this.storageMode = StorageMode.LOCAL_API;
      console.error("Detected DGROO_FAST_API_ENDPOINT, using Local API mode.");
    } else if (openaiApiKey) {
      this.storageMode = StorageMode.IN_MEMORY;
      console.error("Detected OPENAI_API_KEY (and no DGROO_FAST_API_ENDPOINT), using In-Memory mode.");
    } else {
      console.error("Error: Required environment variables not set.");
      console.error("Please set either DGROO_FAST_API_ENDPOINT (for Local API mode) or OPENAI_API_KEY (for In-Memory mode).");
      process.exit(1);
    }
    
    // Initialize MCP Server
    this.server = new Server(
      {
        // These should match package.json
        name: "@dangeroo/mem0-mcp",
        version: "0.1.0",
      },
      {
        capabilities: {
          // Only tools capability needed for now
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.initializeClient();
    
    process.on('SIGINT', async () => {
      console.error("Received SIGINT signal, shutting down...");
      // Restore original console.log before exit
      safeLogger.restore();
      await this.server.close();
      process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
      console.error("Received SIGTERM signal, shutting down...");
      // Restore original console.log before exit
      safeLogger.restore();
      await this.server.close();
      process.exit(0);
    });
    
    // Cleanup on uncaught exceptions
    process.on('uncaughtException', (error) => {
      console.error("Uncaught exception:", error);
      // Restore original console.log before exit
      safeLogger.restore();
      process.exit(1);
    });
  }

  /**
   * Initialize the appropriate client based on the storage mode
   */
  private initializeClient(): void {
    console.error(`Initializing client with storage mode: ${this.storageMode}`);
    
    switch (this.storageMode) {
      case StorageMode.LOCAL_API:
        this.initializeLocalApiClient();
        break;
        
      case StorageMode.IN_MEMORY:
        this.initializeInMemoryClient();
        break;
        
      default:
        // This case should not be reachable due to constructor logic
        console.error(`Critical Error: Reached default case in initializeClient with mode ${this.storageMode}`);
        process.exit(1);
    }
  }
  
  // initializeCloudClient removed as cloud mode is deprecated
  /**
   * Initialize the local API client
   */
  private initializeLocalApiClient(): void {
    const apiEndpoint = process.env.DGROO_FAST_API_ENDPOINT;
    
    if (!apiEndpoint) {
      // This check is technically redundant due to constructor logic, but kept for safety
      console.error("Error: DGROO_FAST_API_ENDPOINT is required for local API mode");
      process.exit(1);
    }
    
    console.error(`Using local API mode with endpoint: ${apiEndpoint}`);
    
    try {
      this.localApiClient = new LocalApiClient(apiEndpoint);
      this.isReady = true;
      console.error("Local API client initialized successfully");
    } catch (error) {
      console.error("Error initializing local API client:", error);
      process.exit(1);
    }
  }
  
  /**
   * Initialize the in-memory client
   */
  private initializeInMemoryClient(): void {
    const openaiApiKey = process.env.OPENAI_API_KEY;
    
    if (!openaiApiKey) {
      console.error("Error: OPENAI_API_KEY is required for in-memory storage mode");
      process.exit(1);
    }
    
    console.error("Using in-memory storage mode with OPENAI_API_KEY");
    
    try {
      // Initialize with silent options if available
      this.localClient = new Memory({
        vectorStore: {
          provider: "memory",
          config: {
            collectionName: "mem0_default_collection"
          }
        }
        // Add silent options if supported by the mem0ai library
        // Options like debug, silent, verbose don't exist in the type but might be supported at runtime
      });
      console.error("In-memory client initialized successfully");
      this.isReady = true;
    } catch (error: any) {
      console.error("Error initializing in-memory client:", error);
      process.exit(1);
    }
  }

  /**
   * Sets up handlers for MCP tool-related requests.
   */
  private setupToolHandlers(): void {
    // Handler for listing available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "add_memory",
            description: "Stores a piece of text as a memory in Mem0.",
            inputSchema: {
              type: "object",
              properties: {
                content: {
                  type: "string",
                  description: "The text content to store as memory.",
                },
                userId: {
                  type: "string",
                  description: "User ID to associate with the memory.",
                },
                sessionId: {
                  type: "string",
                  description: "Optional session ID to associate with the memory.",
                },
                agentId: {
                  type: "string",
                  description: "Optional agent ID to associate with the memory.",
                },
                metadata: {
                  type: "object",
                  description: "Optional key-value metadata.",
                },
              },
              required: ["content", "userId"],
            },
          },
          {
            name: "search_memory",
            description: "Searches stored memories in Mem0 based on a query.",
            inputSchema: {
              type: "object",
              properties: {
                query: {
                  type: "string",
                  description: "The search query.",
                },
                userId: {
                  type: "string",
                  description: "User ID to filter search.",
                },
                sessionId: {
                  type: "string",
                  description: "Optional session ID to filter search.",
                },
                agentId: {
                  type: "string",
                  description: "Optional agent ID to filter search.",
                },
                filters: {
                  type: "object",
                  description: "Optional key-value filters for metadata.",
                },
                threshold: {
                  type: "number",
                  description: "Optional similarity threshold for results.", // Note: Threshold might be specific to implementation
                },
              },
              required: ["query", "userId"],
            },
          },
          {
            name: "delete_memory",
            description: "Deletes a specific memory from Mem0 by ID.",
            inputSchema: {
              type: "object",
              properties: {
                memoryId: {
                  type: "string",
                  description: "The unique ID of the memory to delete.",
                },
                userId: {
                  type: "string",
                  description: "User ID associated with the memory.",
                },
                sessionId: {
                  type: "string",
                  description: "Optional session ID associated with the memory.",
                },
                agentId: {
                  type: "string",
                  description: "Optional agent ID associated with the memory.",
                },
              },
              required: ["memoryId", "userId"],
            },
          },
        ],
      };
    });

    // Handler for call tool requests
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (!this.isReady) {
        throw new McpError(ErrorCode.InternalError, "Memory client is still initializing. Please try again in a moment.");
      }

      try {
        const { name } = request.params;
        const args = request.params.arguments || {};

        if (name === "add_memory") {
          const toolArgs = args as unknown as Mem0AddToolArgs;
          return await this.handleAddMemory(toolArgs);
        } else if (name === "search_memory") {
          const toolArgs = args as unknown as Mem0SearchToolArgs;
          return await this.handleSearchMemory(toolArgs);
        } else if (name === "delete_memory") {
          const toolArgs = args as unknown as Mem0DeleteToolArgs;
          return await this.handleDeleteMemory(toolArgs);
        } else {
          throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
        }
      } catch (error: any) {
        if (error instanceof McpError) {
          throw error;
        }
        
        console.error(`Error executing tool:`, error);
        throw new McpError(ErrorCode.InternalError, `Error executing tool: ${error.message || 'Unknown error'}`);
      }
    });
  }

  /**
   * Handles adding a memory using the appropriate client based on storage mode
   */
  private async handleAddMemory(args: Mem0AddToolArgs): Promise<any> {
    const { content, userId, sessionId, agentId, metadata } = args;

    if (!content) {
      throw new McpError(ErrorCode.InvalidParams, "Missing required argument: content");
    }

    if (!userId) {
      throw new McpError(ErrorCode.InvalidParams, "Missing required argument: userId");
    }

    console.error(`Adding memory for user ${userId} using ${this.storageMode} mode`);
    
    // Format message for all client types
    const messages: Mem0Message[] = [{ 
      role: "user", 
      content 
    }];
    
    try {
      switch (this.storageMode) {
        case StorageMode.LOCAL_API:
          return await this.handleLocalApiAddMemory(messages, userId, sessionId, agentId, metadata);
          
        case StorageMode.IN_MEMORY:
          return await this.handleInMemoryAddMemory(messages, userId, sessionId, metadata);
          
        default:
          // Should not be reachable
          throw new McpError(ErrorCode.InternalError, `Invalid storage mode encountered in handleAddMemory: ${this.storageMode}`);
      }
    } catch (error: any) {
      console.error(`Error adding memory using ${this.storageMode} mode:`, error);
      throw new McpError(ErrorCode.InternalError, `Error adding memory: ${error.message}`);
    }
  }
  
  // handleCloudAddMemory removed as cloud mode is deprecated
  /**
   * Add memory using local API client
   */
  private async handleLocalApiAddMemory(
    messages: Mem0Message[], 
    userId: string, 
    sessionId?: string, 
    agentId?: string, 
    metadata?: Record<string, any>
  ): Promise<any> {
    if (!this.localApiClient) {
      throw new McpError(ErrorCode.InternalError, "Local API client is not initialized");
    }
    
    // Local API options
    const options: any = {
      userId,
      sessionId,
      agentId,
      metadata
    };
    
    // API call
    const result = await this.localApiClient.add(messages, options);
    console.error("Memory added successfully using local API");
    
    return {
      content: [{ type: "text", text: `Memory added successfully` }],
    };
  }
  
  /**
   * Add memory using in-memory client
   */
  private async handleInMemoryAddMemory(
    messages: Mem0Message[], 
    userId: string, 
    sessionId?: string, 
    metadata?: Record<string, any>
  ): Promise<any> {
    if (!this.localClient) {
      throw new McpError(ErrorCode.InternalError, "In-memory client is not initialized");
    }
    
    // Local storage options - using camelCase
    const options: any = {
      userId,
      sessionId,
      metadata
    };
    
    // API call
    const result = await this.localClient.add(messages, options);
    console.error("Memory added successfully using in-memory storage");
    
    return {
      content: [{ type: "text", text: `Memory added successfully` }],
    };
  }

  /**
   * Handles searching memories using the appropriate client based on storage mode
   */
  private async handleSearchMemory(args: Mem0SearchToolArgs): Promise<any> {
    const { query, userId, sessionId, agentId, filters, threshold } = args;

    if (!query) {
      throw new McpError(ErrorCode.InvalidParams, "Missing required argument: query");
    }

    if (!userId) {
      throw new McpError(ErrorCode.InvalidParams, "Missing required argument: userId");
    }

    console.error(`Searching memories for query "${query}" and user ${userId} using ${this.storageMode} mode`);
    
    try {
      switch (this.storageMode) {
        case StorageMode.LOCAL_API:
          // Note: Threshold might not be supported by dgroo-fast-api, passing it for now.
          return await this.handleLocalApiSearchMemory(query, userId, sessionId, agentId, filters);
          
        case StorageMode.IN_MEMORY:
          // Note: Threshold is not directly supported by mem0ai oss Memory.search
          return await this.handleInMemorySearchMemory(query, userId, sessionId, filters);
          
        default:
           // Should not be reachable
          throw new McpError(ErrorCode.InternalError, `Invalid storage mode encountered in handleSearchMemory: ${this.storageMode}`);
      }
    } catch (error: any) {
      console.error(`Error searching memories using ${this.storageMode} mode:`, error);
      throw new McpError(ErrorCode.InternalError, `Error searching memories: ${error.message}`);
    }
  }
  
  // handleCloudSearchMemory removed as cloud mode is deprecated
  /**
   * Search memory using local API client
   */
  private async handleLocalApiSearchMemory(
    query: string, 
    userId: string, 
    sessionId?: string, 
    agentId?: string, 
    filters?: Record<string, any>
  ): Promise<any> {
    if (!this.localApiClient) {
      throw new McpError(ErrorCode.InternalError, "Local API client is not initialized");
    }
    
    // Local API options
    const options: any = {
      userId,
      sessionId,
      agentId,
      filters
    };
    
    // API call
    const results = await this.localApiClient.search(query, options);
    console.error(`Found memories using local API`);
    
    return {
      content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
    };
  }
  
  /**
   * Search memory using in-memory client
   */
  private async handleInMemorySearchMemory(
    query: string, 
    userId: string, 
    sessionId?: string, 
    filters?: Record<string, any>
  ): Promise<any> {
    if (!this.localClient) {
      throw new McpError(ErrorCode.InternalError, "In-memory client is not initialized");
    }
    
    // Local storage options
    const options: any = {
      userId,
      sessionId,
      filters
    };
    
    // API call
    const results = await this.localClient.search(query, options);
    
    // Handle potential array or object result
    const resultsArray = Array.isArray(results) ? results : [results];
    console.error(`Found ${resultsArray.length} memories using in-memory storage`);
    
    return {
      content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
    };
  }

  /**
   * Handles deleting a memory by ID using the appropriate client based on storage mode
   */
  private async handleDeleteMemory(args: Mem0DeleteToolArgs): Promise<any> {
    const { memoryId, userId, sessionId, agentId } = args;

    if (!memoryId) {
      throw new McpError(ErrorCode.InvalidParams, "Missing required argument: memoryId");
    }

    if (!userId) {
      throw new McpError(ErrorCode.InvalidParams, "Missing required argument: userId");
    }

    console.error(`Deleting memory with ID ${memoryId} for user ${userId} using ${this.storageMode} mode`);
    
    try {
      switch (this.storageMode) {
        case StorageMode.LOCAL_API:
          // Pass userId, sessionId, agentId if the dgroo-fast-api delete endpoint uses them for authorization/filtering
          return await this.handleLocalApiDeleteMemory(memoryId, userId, sessionId, agentId);
          
        case StorageMode.IN_MEMORY:
          // In-memory delete likely only needs memoryId
          return await this.handleInMemoryDeleteMemory(memoryId);
          
        default:
           // Should not be reachable
          throw new McpError(ErrorCode.InternalError, `Invalid storage mode encountered in handleDeleteMemory: ${this.storageMode}`);
      }
    } catch (error: any) {
      console.error(`Error deleting memory using ${this.storageMode} mode:`, error);
      throw new McpError(ErrorCode.InternalError, `Error deleting memory: ${error.message}`);
    }
  }
  
  // handleCloudDeleteMemory removed as cloud mode is deprecated
  /**
   * Delete memory using local API client (dgroo-fast-api)
   */
  private async handleLocalApiDeleteMemory(
    memoryId: string,
    userId: string,
    sessionId?: string,
    agentId?: string
  ): Promise<any> {
    if (!this.localApiClient) {
      throw new McpError(ErrorCode.InternalError, "Local API client is not initialized");
    }
    
    // Pass relevant identifiers if needed by the API endpoint
    const options = { userId, sessionId, agentId };
    
    // API call - adjust parameters based on dgroo-fast-api requirements
    await this.localApiClient.delete(memoryId, options);
    console.error(`Memory ${memoryId} deleted successfully using local API`);
    
    return {
      content: [{ type: "text", text: `Memory ${memoryId} deleted successfully` }],
    };
  }
  
  /**
   * Delete memory using in-memory client
   */
  private async handleInMemoryDeleteMemory(memoryId: string): Promise<any> {
    if (!this.localClient) {
      throw new McpError(ErrorCode.InternalError, "In-memory client is not initialized");
    }
    
    // The local client's delete method only takes memoryId as a parameter
    await this.localClient.delete(memoryId);
    console.error(`Memory ${memoryId} deleted successfully using in-memory storage`);
    
    return {
      content: [{ type: "text", text: `Memory ${memoryId} deleted successfully` }],
    };
  }

  /**
   * Starts the MCP server.
   */
  public async start(): Promise<void> {
    console.error(`Starting Dangeroo Mem0 MCP Server in ${this.storageMode} mode...`);
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Mem0 MCP Server is running.");
  }
}

// Start the server
const server = new Mem0MCPServer();
server.start().catch((error) => {
  console.error("Failed to start server:", error);
  // Restore original console.log before exit
  safeLogger.restore();
  process.exit(1);
});