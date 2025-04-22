#!/usr/bin/env node

/**
 * Simple test script for Mem0 MCP server
 * 
 * This script:
 * 1. Connects to the Mem0 API server
 * 2. Adds a memory
 * 3. Waits 10 seconds
 * 4. Searches for the memory
 */

const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

// Configuration
const API_URL = 'http://localhost:8888';
const USER_ID = 'dangeroo-agent' + uuidv4().substring(0, 8);
const MEMORY_CONTENT = 'The capital of France is Paris. It is known for the Eiffel Tower.';

console.log(`=== Mem0 API Server Test ===`);
console.log(`Using API at: ${API_URL}`);
console.log(`Using User ID: ${USER_ID}`);

// Helper function to log detailed error information
function logDetailedError(error, context) {
  console.error(`❌ ${context}: ${error.message}`);
  
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    console.error('Status:', error.response.status);
    console.error('Headers:', JSON.stringify(error.response.headers, null, 2));
    console.error('Response data:', JSON.stringify(error.response.data, null, 2));
  } else if (error.request) {
    // The request was made but no response was received
    console.error('No response received:', error.request);
  } else {
    // Something happened in setting up the request that triggered an Error
    console.error('Error during request setup:', error.message);
  }
  console.error('Error config:', JSON.stringify(error.config, null, 2));
}

// Define test functions
async function checkApiHealth() {
  try {
    console.log('\n🔍 Checking API health...');
    const response = await axios.get(`${API_URL}/health`);
    console.log(`✅ API health check result: ${JSON.stringify(response.data)}`);
    return response.data;
  } catch (error) {
    logDetailedError(error, 'API health check failed');
    process.exit(1);
  }
}

async function addMemory() {
  try {
    console.log('\n📝 Adding memory...');
    const payload = {
      messages: [
        {
          role: 'user',
          content: MEMORY_CONTENT
        }
      ],
      user_id: USER_ID
    };
    
    console.log('Request payload:', JSON.stringify(payload, null, 2));
    const response = await axios.post(`${API_URL}/memories`, payload);
    console.log(`✅ Memory added successfully!`);
    console.log('Response:', JSON.stringify(response.data, null, 2));
    
    return response.data;
  } catch (error) {
    logDetailedError(error, 'Failed to add memory');
    process.exit(1);
  }
}

async function searchMemory() {
  try {
    console.log('\n🔍 Searching memory...');
    const payload = {
      query: 'What is the capital of France?',
      user_id: USER_ID
      // Don't add custom filters - let mem0 handle this automatically
    };
    
    console.log('Search payload:', JSON.stringify(payload, null, 2));
    const response = await axios.post(`${API_URL}/search`, payload);
    console.log(`✅ Memory search successful!`);
    console.log('Search Results:', JSON.stringify(response.data, null, 2));
    
    return response.data;
  } catch (error) {
    logDetailedError(error, 'Failed to search memory');
    process.exit(1);
  }
}

async function getAllMemories() {
  try {
    console.log('\n📋 Getting all memories...');
    const response = await axios.get(`${API_URL}/memories?user_id=${USER_ID}`);
    console.log(`✅ Successfully retrieved all memories!`);
    console.log('Memories:', JSON.stringify(response.data, null, 2));
    
    return response.data;
  } catch (error) {
    logDetailedError(error, 'Failed to get all memories');
    process.exit(1);
  }
}

// Main execution
async function runTest() {
  console.log('\n🚀 Starting Mem0 test...');
  
  // Check API health
  await checkApiHealth();
  
  // Add memory
  const addResult = await addMemory();
  
  // Wait for 10 seconds
  console.log('\n⏳ Waiting for 10 seconds...');
  await new Promise(resolve => setTimeout(resolve, 10000));
  
  // Get all memories
  const allMemories = await getAllMemories();
  
  // Search for memory
  const searchResult = await searchMemory();
  
  console.log('\n✅ Test completed successfully!');
  console.log(`Total memories found: ${allMemories.results ? allMemories.results.length : 0}`);
  console.log(`Search results found: ${searchResult.results ? searchResult.results.length : 0}`);
}

// Run the test
runTest().catch(error => {
  console.error(`❌ Test failed with error: ${error.message}`);
  process.exit(1);
});