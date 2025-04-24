#!/usr/bin/env node

/**
 * Script to check the debug endpoint of the Mem0 API server
 */

const axios = require('axios');

// Configuration
const API_URL = 'http://localhost:8888';

async function checkDebugEndpoint() {
  try {
    console.log('Calling debug endpoint...');
    const response = await axios.get(`${API_URL}/debug`);
    console.log('Debug information:');
    console.log(JSON.stringify(response.data, null, 2));
    
    // Check for potential issues
    const config = response.data.config;
    const connections = response.data.connections;
    
    // Check if memory instance is initialized
    if (!config.memory_instance) {
      console.log('\n⚠️  Warning: Memory instance is not initialized!');
    }
    
    // Check vector store connection
    if (connections.vector_store && !connections.vector_store.connected) {
      console.log('\n⚠️  Warning: Vector store connection failed!');
      console.log('Error:', connections.vector_store.error);
    }
    
    // Check graph store connection
    if (connections.graph_store && !connections.graph_store.connected) {
      console.log('\n⚠️  Warning: Graph store connection failed!');
      console.log('Error:', connections.graph_store.error);
    }
    
    // Check if vector store host is using Docker service name (which won't work)
    if (config.vector_store.host === 'chroma') {
      console.log('\n⚠️  Warning: Vector store host is set to "chroma"!');
      console.log('This Docker service name will only work inside the container network.');
      console.log('For inter-container communication, use localhost or the actual IP address.');
    }
    
    console.log('\nAnalysis complete.');
    
  } catch (error) {
    console.error('Error calling debug endpoint:', error.message);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

checkDebugEndpoint();