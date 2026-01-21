#!/usr/bin/env node

/**
 * Test script for MCP integration
 * Tests BrightData and Fetch MCP server integration
 */

const { spawn } = require('child_process');
const http = require('http');

console.log('Testing MCP integration...');

// Start the bridge server
console.log('Starting bridge server...');
const serverProcess = spawn('node', ['bridge-server.js'], {
  cwd: __dirname,
  stdio: ['pipe', 'pipe', 'pipe']
});

let serverReady = false;

// Handle server output
serverProcess.stdout.on('data', (data) => {
  const output = data.toString();
  console.log('Server output:', output);
  if (output.includes('Bridge Server running')) {
    serverReady = true;
  }
});

serverProcess.stderr.on('data', (data) => {
  console.error('Server error:', data.toString());
});

serverProcess.on('close', (code) => {
  console.log(`Server process exited with code ${code}`);
});

// Wait for server to start, then test endpoints
setTimeout(async () => {
  if (!serverReady) {
    console.log('Server not ready, waiting longer...');
    setTimeout(() => runTests(), 5000);
  } else {
    runTests();
  }
}, 3000);

async function runTests() {
  console.log('\n=== Running MCP Integration Tests ===\n');

  try {
    // Test 1: Health check
    console.log('Test 1: Health check...');
    const healthResponse = await makeRequest('/health');
    console.log('Health response:', JSON.stringify(healthResponse, null, 2));

    // Test 2: Fetch MCP integration
    console.log('\nTest 2: Fetch MCP integration...');
    const fetchResponse = await makeRequest('/api/v1/fetch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: 'https://httpbin.org/get',
        method: 'GET'
      })
    });
    console.log('Fetch response:', JSON.stringify(fetchResponse, null, 2));

    // Test 3: BrightData search
    console.log('\nTest 3: BrightData search...');
    const brightdataResponse = await makeRequest('/api/v1/brightdata/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: 'test search query',
        options: { limit: 3 }
      })
    });
    console.log('BrightData response:', JSON.stringify(brightdataResponse, null, 2));

    // Test 4: BrightData scrape
    console.log('\nTest 4: BrightData scrape...');
    const scrapeResponse = await makeRequest('/api/v1/brightdata/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: 'https://httpbin.org/html',
        options: {}
      })
    });
    console.log('BrightData scrape response:', JSON.stringify(scrapeResponse, null, 2));

  } catch (error) {
    console.error('Test failed:', error.message);
  } finally {
    console.log('\n=== Tests completed ===');
    // Shutdown server
    serverProcess.kill();
    process.exit(0);
  }
}

function makeRequest(path, options = {}) {
  return new Promise((resolve, reject) => {
    const reqOptions = {
      hostname: 'localhost',
      port: 8001,
      path: path,
      method: options.method || 'GET',
      headers: options.headers || {}
    };

    const req = http.request(reqOptions, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve(jsonData);
        } catch (e) {
          resolve(data); // Return raw data if not JSON
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (options.body) {
      req.write(options.body);
    }

    req.end();
  });
}
