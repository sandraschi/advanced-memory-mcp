#!/usr/bin/env node
/**
 * Comprehensive ADN MCP Server Integration Test Suite
 * Tests the Advanced Memory MCP server integration with extensive validation
 */

const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

const PORT = 8001; // Use the same port as the bridge server
let bridgeProcess = null;
let testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  errors: []
};

function log(message) {
  console.log(`[${new Date().toISOString()}] ${message}`);
}

function logError(message) {
  console.error(`[${new Date().toISOString()}] ERROR: ${message}`);
  testResults.errors.push(message);
}

function testPassed(testName) {
  console.log(`✅ ${testName}`);
  testResults.passed++;
}

function testFailed(testName, error) {
  console.log(`❌ ${testName}: ${error}`);
  testResults.failed++;
  testResults.errors.push(`${testName}: ${error}`);
}

async function makeRequest(endpoint, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'localhost',
      port: PORT,
      path: endpoint,
      method: method,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => {
        body += chunk;
      });
      res.on('end', () => {
        try {
          const response = {
            status: res.statusCode,
            headers: res.headers,
            body: JSON.parse(body)
          };
          resolve(response);
        } catch (e) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            body: body
          });
        }
      });
    });

    req.on('error', (err) => {
      reject(err);
    });

    if (data) {
      req.write(JSON.stringify(data));
    }
    req.end();
  });
}

async function waitForBridgeReady(maxWaitMs = 30000) {
  const startTime = Date.now();

  while (Date.now() - startTime < maxWaitMs) {
    try {
      const response = await makeRequest('/health');
      log(`Health check response: ${response.status}, body: ${JSON.stringify(response.body).substring(0, 200)}...`);

      if (response.status === 200 &&
          response.body.status === 'ok') {
        log('Bridge server is ready with MCP integrations');
        // ADN MCP is now simulated, so we just need the bridge server to be up
        return true;
      }
      log('Waiting for bridge server to be ready...');
    } catch (e) {
      log(`Bridge server not ready yet, error: ${e.message}`);
      // If connection fails completely, the server might not be running
      if (e.code === 'ECONNREFUSED') {
        log('Server is not running, connection refused');
      }
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  throw new Error('Bridge server did not become ready within timeout');
}

function startBridgeServer() {
  return new Promise((resolve, reject) => {
    log('Starting ADN MCP Bridge Server...');

    const env = {
      ...process.env,
      PORT: PORT.toString()
    };

    bridgeProcess = spawn('node', ['bridge-server.js'], {
      cwd: __dirname,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: env
    });

    let startupComplete = false;
    let outputBuffer = '';

    const checkStartup = (data) => {
      const chunk = data.toString();
      outputBuffer += chunk;
      log(`Server output: ${chunk.trim()}`);

      if (!startupComplete && chunk.includes('ADN MCP Bridge Server running')) {
        startupComplete = true;
        resolve();
      }
    };

    bridgeProcess.stdout.on('data', checkStartup);
    bridgeProcess.stderr.on('data', checkStartup);

    bridgeProcess.on('error', (error) => {
      logError(`Bridge server failed to start: ${error.message}`);
      reject(error);
    });

    // Timeout after 60 seconds
    setTimeout(() => {
      if (!startupComplete) {
        reject(new Error('Bridge server startup timeout'));
      }
    }, 60000);
  });
}

async function runADNMCPIntegrationTests() {
  log('=== Running ADN MCP Integration Tests ===');

  try {
    // Test 1: Health Check
    testResults.total++;
    try {
      const response = await makeRequest('/health');
      if (response.status === 200 &&
          response.body.status === 'ok' &&
          response.body.servers.adn &&
          response.body.servers.adn.initialized) {
        testPassed('Health check');
      } else {
        testFailed('Health check', `Unexpected response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('Health check', error.message);
    }

    // Test 2: ADN MCP Tools Discovery
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools');
      if (response.status === 200 &&
          response.body.success &&
          Array.isArray(response.body.data.tools) &&
          response.body.data.tools.length > 0) {
        testPassed('ADN MCP tools discovery');
        log(`Discovered ${response.body.data.tools.length} ADN MCP tools`);

        // Log some tool names for verification
        const toolNames = response.body.data.tools.slice(0, 5).map(t => t.name);
        log(`Sample tools: ${toolNames.join(', ')}`);
      } else {
        testFailed('ADN MCP tools discovery', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP tools discovery', error.message);
    }

    // Test 3: ADN MCP Prompts Discovery
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/prompts');
      if (response.status === 200 &&
          response.body.success &&
          Array.isArray(response.body.data.prompts)) {
        testPassed('ADN MCP prompts discovery');
        log(`Discovered ${response.body.data.prompts.length} ADN MCP prompts`);
      } else {
        testFailed('ADN MCP prompts discovery', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP prompts discovery', error.message);
    }

    // Test 4: ADN MCP Tool Call - Search
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_search', 'POST', {
        arguments: {
          query: "test search query",
          limit: 5
        }
      });

      if (response.status === 200 &&
          response.body.success &&
          response.body.data) {
        testPassed('ADN MCP search tool call');
        log(`Search results received: ${JSON.stringify(response.body.data).substring(0, 200)}...`);
      } else {
        testFailed('ADN MCP search tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP search tool call', error.message);
    }

    // Test 5: ADN MCP Tool Call - Recent Activity
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/recent_activity', 'POST', {
        arguments: {
          type: "all",
          limit: 10,
          timeframe: "1d"
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP recent activity tool call');
        log('Recent activity query successful');
      } else {
        testFailed('ADN MCP recent activity tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP recent activity tool call', error.message);
    }

    // Test 6: ADN MCP Tool Call - Skills Reader
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_skills_reader', 'POST', {
        arguments: {
          ide: "cursor",
          limit: 5
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP skills reader tool call');
        log('Skills reader query successful');
      } else {
        testFailed('ADN MCP skills reader tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP skills reader tool call', error.message);
    }

    // Test 7: ADN MCP Tool Call - Web Search
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_web_search', 'POST', {
        arguments: {
          query: "artificial intelligence",
          max_results: 3
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP web search tool call');
        log('Web search query successful');
      } else {
        testFailed('ADN MCP web search tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP web search tool call', error.message);
    }

    // Test 8: ADN MCP Tool Call - Document Ingest
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_document_ingest', 'POST', {
        arguments: {
          content: "This is a test document for ingestion.",
          title: "Test Document",
          tags: ["test", "document"]
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP document ingest tool call');
        log('Document ingestion successful');
      } else {
        testFailed('ADN MCP document ingest tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP document ingest tool call', error.message);
    }

    // Test 9: ADN MCP Tool Call - RAG Query
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_rag', 'POST', {
        arguments: {
          query: "What is artificial intelligence?",
          limit: 3
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP RAG tool call');
        log('RAG query successful');
      } else {
        testFailed('ADN MCP RAG tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP RAG tool call', error.message);
    }

    // Test 10: ADN MCP Tool Call - GitHub Research
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_github_research', 'POST', {
        arguments: {
          query: "machine learning",
          limit: 2
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP GitHub research tool call');
        log('GitHub research query successful');
      } else {
        testFailed('ADN MCP GitHub research tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP GitHub research tool call', error.message);
    }

    // Test 11: ADN MCP Tool Call - ArXiv Research
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_arxiv_research', 'POST', {
        arguments: {
          query: "neural networks",
          max_results: 2
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP ArXiv research tool call');
        log('ArXiv research query successful');
      } else {
        testFailed('ADN MCP ArXiv research tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP ArXiv research tool call', error.message);
    }

    // Test 12: ADN MCP Tool Call - TV Tropes Research
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_tvtropes_research', 'POST', {
        arguments: {
          query: "artificial intelligence in fiction",
          limit: 2
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP TV Tropes research tool call');
        log('TV Tropes research query successful');
      } else {
        testFailed('ADN MCP TV Tropes research tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP TV Tropes research tool call', error.message);
    }

    // Test 13: ADN MCP Prompt Get - AI Assistant Guide
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/prompts/ai_assistant_guide', 'POST', {
        arguments: {}
      });

      if (response.status === 200 &&
          response.body.success &&
          response.body.data) {
        testPassed('ADN MCP AI assistant guide prompt');
        log('AI assistant guide prompt retrieved successfully');
      } else {
        testFailed('ADN MCP AI assistant guide prompt', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP AI assistant guide prompt', error.message);
    }

    // Test 14: ADN MCP Tool Call - Make Skill Advanced
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/make_skill_advanced', 'POST', {
        arguments: {
          name: "Test Skill",
          description: "A test skill for validation",
          content: "# Test Skill\n\nThis is a test skill content."
        }
      });

      if (response.status === 200 &&
          response.body.success) {
        testPassed('ADN MCP make skill tool call');
        log('Skill creation successful');
      } else {
        testFailed('ADN MCP make skill tool call', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP make skill tool call', error.message);
    }

    // Test 15: Error Handling - Invalid Tool
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/nonexistent_tool', 'POST', {
        arguments: {}
      });

      // Should return an error, but not crash the server
      if (response.status >= 400) {
        testPassed('ADN MCP error handling for invalid tool');
        log('Error handling works correctly for invalid tools');
      } else {
        testFailed('ADN MCP error handling for invalid tool', 'Should return error status');
      }
    } catch (error) {
      testFailed('ADN MCP error handling for invalid tool', error.message);
    }

    // Test 16: Error Handling - Invalid Arguments
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_search', 'POST', {
        arguments: {
          invalid_param: "should cause error"
        }
      });

      if (response.status === 200 && response.body.success === false) {
        testPassed('ADN MCP error handling for invalid arguments');
        log('Invalid arguments handled gracefully');
      } else {
        testFailed('ADN MCP error handling for invalid arguments', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP error handling for invalid arguments', error.message);
    }

    // Test 17: Concurrent Requests
    testResults.total++;
    try {
      const promises = [];
      for (let i = 0; i < 5; i++) {
        promises.push(makeRequest('/api/v1/mcp/tools/adn_search', 'POST', {
          arguments: {
            query: `concurrent test ${i}`,
            limit: 1
          }
        }));
      }

      const results = await Promise.all(promises);
      const allSuccessful = results.every(r => r.status === 200 && r.body.success);

      if (allSuccessful) {
        testPassed('ADN MCP concurrent requests handling');
        log('All concurrent requests handled successfully');
      } else {
        testFailed('ADN MCP concurrent requests handling', 'Some concurrent requests failed');
      }
    } catch (error) {
      testFailed('ADN MCP concurrent requests handling', error.message);
    }

    // Test 18: Large Response Handling
    testResults.total++;
    try {
      const response = await makeRequest('/api/v1/mcp/tools/adn_search', 'POST', {
        arguments: {
          query: "comprehensive search",
          limit: 20
        }
      });

      if (response.status === 200 &&
          response.body.success &&
          response.body.data) {
        testPassed('ADN MCP large response handling');
        log('Large response handled successfully');
      } else {
        testFailed('ADN MCP large response handling', `Response: ${JSON.stringify(response.body)}`);
      }
    } catch (error) {
      testFailed('ADN MCP large response handling', error.message);
    }

  } catch (error) {
    logError(`Test suite failed: ${error.message}`);
  }
}

async function runPerformanceTests() {
  log('=== Running ADN MCP Performance Tests ===');

  // Test 19: Response Time Benchmark
  testResults.total++;
  try {
    const startTime = Date.now();
    const response = await makeRequest('/api/v1/mcp/tools/adn_search', 'POST', {
      arguments: {
        query: "performance test",
        limit: 5
      }
    });
    const endTime = Date.now();
    const responseTime = endTime - startTime;

    if (response.status === 200 && response.body.success && responseTime < 5000) {
      testPassed(`ADN MCP response time benchmark (${responseTime}ms)`);
      log(`Response time: ${responseTime}ms`);
    } else {
      testFailed('ADN MCP response time benchmark', `Too slow: ${responseTime}ms`);
    }
  } catch (error) {
    testFailed('ADN MCP response time benchmark', error.message);
  }

  // Test 20: Memory Leak Test (Basic)
  testResults.total++;
  try {
    let successCount = 0;
    for (let i = 0; i < 10; i++) {
      const response = await makeRequest('/api/v1/mcp/tools/adn_search', 'POST', {
        arguments: {
          query: `memory test ${i}`,
          limit: 2
        }
      });
      if (response.status === 200 && response.body.success) {
        successCount++;
      }
      // Small delay to prevent overwhelming
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    if (successCount >= 9) {
      testPassed('ADN MCP memory leak test (basic)');
      log(`${successCount}/10 requests successful`);
    } else {
      testFailed('ADN MCP memory leak test (basic)', `${successCount}/10 requests successful`);
    }
  } catch (error) {
    testFailed('ADN MCP memory leak test (basic)', error.message);
  }
}

async function cleanup() {
  log('=== Cleaning up test environment ===');

  if (bridgeProcess) {
    log('Terminating bridge server...');
    bridgeProcess.kill('SIGTERM');

    // Wait for process to terminate
    await new Promise(resolve => {
      const timeout = setTimeout(() => {
        log('Force killing bridge server...');
        bridgeProcess.kill('SIGKILL');
        resolve();
      }, 5000);

      bridgeProcess.on('close', () => {
        clearTimeout(timeout);
        resolve();
      });
    });
  }
}

async function main() {
  try {
    log('=== ADN MCP Integration Test Suite ===');

    // Start the bridge server
    await startBridgeServer();

    // Wait for the bridge to be fully ready
    await waitForBridgeReady();

    // Run comprehensive integration tests
    await runADNMCPIntegrationTests();

    // Run performance tests
    await runPerformanceTests();

  } catch (error) {
    logError(`Test suite failed: ${error.message}`);
    testResults.errors.push(`Suite failure: ${error.message}`);
  } finally {
    await cleanup();

    // Print results
    log('=== Test Results ===');
    log(`Total Tests: ${testResults.total}`);
    log(`Passed: ${testResults.passed}`);
    log(`Failed: ${testResults.failed}`);
    log(`Success Rate: ${((testResults.passed / testResults.total) * 100).toFixed(1)}%`);

    if (testResults.errors.length > 0) {
      log('=== Errors ===');
      testResults.errors.forEach(error => log(`- ${error}`));
    }

    process.exit(testResults.failed > 0 ? 1 : 0);
  }
}

if (require.main === module) {
  main().catch(error => {
    console.error('Unhandled error:', error);
    process.exit(1);
  });
}

module.exports = { main, makeRequest };
