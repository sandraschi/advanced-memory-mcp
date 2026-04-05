#!/usr/bin/env node
/**
 * ADN MCP Bridge Server
 * Bridges stdio MCP communication to HTTP for webapp access
 */

const { spawn } = require('child_process');
const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const PORT = parseInt(process.env.ADN_BRIDGE_PORT, 10) || 10705;

// Repo root is two levels up from webapp/backend/
const REPO_ROOT = path.resolve(__dirname, '..', '..');

// Enable CORS for frontend access
app.use(cors());

app.get('/api/v1/health', (req, res) => {
  res.json({ success: true, status: 'online', adn_bridge: true });
});

app.use(express.json());

// Error handling for JSON parsing
app.use((err, req, res, next) => {
  if (err instanceof SyntaxError && err.status === 400 && 'body' in err) {
    addLog('ERROR', `JSON Parsing Error: ${err.message}. Raw Body: ${req.rawBody}`, 'system');
    return res.status(400).send({ success: false, error: `Malformed JSON: ${err.message}` });
  }
  next();
});

// Store active MCP processes and client state
const mcpProcesses = new Map();
const mcpClients = new Map(); // Map of server names to MCP clients
let nextRequestId = 1;

// Global log buffer for tracking system and MCP logs
const logBuffer = [];
const MAX_LOGS = 1000;

function addLog(level, message, source = 'system') {
  const logEntry = {
    timestamp: new Date().toISOString().replace('T', ' ').split('.')[0],
    level: level.toUpperCase(),
    message: message,
    source: source
  };
  logBuffer.push(logEntry);
  if (logBuffer.length > MAX_LOGS) {
    logBuffer.shift();
  }
  // Also log to console for debugging
  console.log(`[${logEntry.timestamp}] ${logEntry.level} (${source}): ${message}`);
}

// Get skill directory path for a given folder (absolute, resolved)
function getSkillDirectory(folderName) {
  const userHome = process.env.USERPROFILE || process.env.HOME || '';
  if (!userHome && (folderName === 'cursor-skills' || folderName === 'windsurf-skills' || folderName === 'antigravity-skills')) {
    return null;
  }
  let dir;
  switch (folderName) {
    case 'cursor-skills':
      dir = path.join(userHome, '.cursor', 'skills-cursor');
      break;
    case 'windsurf-skills':
      dir = path.join(userHome, '.codeium', 'windsurf', 'skills');
      break;
    case 'adn-skills':
      dir = path.join(REPO_ROOT, 'skills');
      break;
    case 'antigravity-skills':
      dir = path.join(userHome, '.gemini', 'antigravity', 'skills');
      break;
    default:
      return null;
  }
  return path.resolve(dir);
}

// Scan skill directory for SKILL.md files (recursive for nested layouts e.g. adn skills/creative/<skill>/SKILL.md)
async function scanSkillDirectory(skillDir, folderName) {
  const skills = [];

  function safeFilePath(skillMdPath, dirName) {
    try {
      const rel = path.relative(REPO_ROOT, skillMdPath);
      if (!rel.startsWith('..') && !path.isAbsolute(rel)) return rel;
    } catch (_) { /* cross-drive etc. */ }
    return path.join(folderName, dirName, 'SKILL.md');
  }

  async function scanDir(dir) {
    let entries;
    try {
      entries = await fs.readdir(dir, { withFileTypes: true });
    } catch (e) {
      return;
    }
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const skillPath = path.join(dir, entry.name);
      const skillMdPath = path.join(skillPath, 'SKILL.md');
      try {
        await fs.access(skillMdPath);
        const raw = await fs.readFile(skillMdPath, 'utf8');
        const content = raw.trimStart();
        const skillData = parseSkillFrontmatter(content, folderName, entry.name);
        if (skillData) {
          skillData.filePath = safeFilePath(skillMdPath, entry.name);
          skills.push(skillData);
        }
      } catch {
        await scanDir(skillPath);
      }
    }
  }

  try {
    await fs.access(skillDir);
    await scanDir(skillDir);
  } catch (_) { }
  return skills;
}

// Parse SKILL.md frontmatter and content; dirName fallback when no frontmatter
function parseSkillFrontmatter(content, folderName, dirName) {
  try {
    const frontmatterMatch = content.match(/^\s*---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/);
    let title = dirName ? dirName.replace(/-/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) : 'Untitled Skill';
    let description = '';
    let tags = [];
    let body = content;

    if (frontmatterMatch) {
      const frontmatter = frontmatterMatch[1];
      body = frontmatterMatch[2].trim();
      const metadata = {};
      const lines = frontmatter.split('\n');
      for (const line of lines) {
        const colonIndex = line.indexOf(':');
        if (colonIndex > 0 && !line.match(/^\s+/)) {
          const key = line.substring(0, colonIndex).trim();
          const value = line.substring(colonIndex + 1).trim().replace(/^["']|["']$/g, '');
          metadata[key] = value;
        }
      }
      title = metadata.name || metadata.title || title;
      description = metadata.description || '';
      tags = metadata.tags ? metadata.tags.split(',').map((t) => t.trim()) : [];
    }

    return {
      id: Date.now() + Math.random(),
      title,
      description,
      folder: folderName,
      tags,
      created: new Date().toISOString(),
      modified: new Date().toISOString(),
      content: body
    };
  } catch (error) {
    return null;
  }
}

// External MCP Client Class - Connects to external MCP servers via MCP tool interface
class ExternalMCPClient {
  constructor(serverName) {
    this.serverName = serverName;
    this.initialized = false;
    this.tools = [];
    this.prompts = [];
  }

  async initialize() {
    try {
      console.log(`Initializing external MCP client for ${this.serverName}...`);

      // Discover available tools from the external server
      this.tools = await this.discoverTools();
      this.prompts = await this.discoverPrompts();

      this.initialized = true;
      console.log(`External MCP client ${this.serverName} initialized with ${this.tools.length} tools and ${this.prompts.length} prompts`);
    } catch (error) {
      console.error(`Failed to initialize external MCP client ${this.serverName}:`, error);
      // Don't throw - allow fallback behavior
      this.tools = [];
      this.prompts = [];
      this.initialized = false;
    }
  }

  async discoverTools() {
    try {
      console.log(`Discovering tools for ${this.serverName}...`);

      // For BrightData
      if (this.serverName === 'brightdata') {
        return [
          { name: 'search_engine', description: 'Search engine with anti-bot bypass' },
          { name: 'scrape_as_markdown', description: 'Scrape web content as markdown' },
          { name: 'search_engine_batch', description: 'Batch search operations' },
          { name: 'scrape_batch', description: 'Batch scraping operations' }
        ];
      }
      // For Fetch
      else if (this.serverName === 'fetch') {
        return [
          { name: 'fetch', description: 'HTTP fetch with advanced options' }
        ];
      }

      return [];
    } catch (error) {
      console.error(`Failed to discover tools for ${this.serverName}:`, error);
      return [];
    }
  }

  async discoverPrompts() {
    // Most external MCP servers focus on tools rather than prompts
    return [];
  }

  async callTool(toolName, args = {}) {
    console.log(`Calling external tool ${this.serverName}/${toolName} with args:`, args);

    try {
      // Use the MCP tool interface to call external MCP servers
      const serverKey = `user-${this.serverName}`;

      // Check if this is a real MCP server we can call
      const availableServers = ['brightdata', 'fetch'];
      if (availableServers.includes(this.serverName)) {
        return await this.callRealMCPTool(toolName, args);
      } else {
        return await this.simulateExternalCall(toolName, args);
      }
    } catch (error) {
      console.error(`External tool call failed ${this.serverName}/${toolName}:`, error);
      // Return error in result format instead of throwing
      return {
        error: error.message,
        tool: toolName,
        server: this.serverName,
        note: 'Tool call failed, but returned error in result format'
      };
    }
  }

  async callRealMCPTool(toolName, args = {}) {
    try {
      console.log(`Making real MCP call to ${this.serverName}/${toolName}`);

      // Use the CallMcpTool function to make actual MCP calls
      // This will use the MCP tool interface to call the external server
      const serverKey = `user-${this.serverName}`;

      // For BrightData tools
      if (this.serverName === 'brightdata') {
        switch (toolName) {
          case 'search_engine':
            // Call the actual BrightData MCP server search tool
            return await this.makeMCPToolCall('brightdata', 'search_engine', {
              query: args.query,
              options: args.options || {}
            });

          case 'scrape_as_markdown':
            // Call the actual BrightData MCP server scrape tool
            return await this.makeMCPToolCall('brightdata', 'scrape_as_markdown', {
              url: args.url,
              options: args.options || {}
            });

          case 'search_engine_batch':
            return await this.makeMCPToolCall('brightdata', 'search_engine_batch', args);

          case 'scrape_batch':
            return await this.makeMCPToolCall('brightdata', 'scrape_batch', args);

          default:
            throw new Error(`Unknown BrightData tool: ${toolName}`);
        }
      }

      // For Fetch tools
      if (this.serverName === 'fetch') {
        switch (toolName) {
          case 'fetch':
            // Call the actual Fetch MCP server
            return await this.makeMCPToolCall('fetch', 'fetch', {
              url: args.url,
              method: args.method || 'GET',
              headers: args.headers || {},
              body: args.body
            });

          default:
            throw new Error(`Unknown Fetch tool: ${toolName}`);
        }
      }

      throw new Error(`Unsupported server: ${this.serverName}`);
    } catch (error) {
      console.error(`Real MCP call failed for ${this.serverName}/${toolName}:`, error);
      addLog('ERROR', `Real MCP call failed for ${this.serverName}/${toolName}: ${error.message}`, this.serverName);
      throw error;
    }
  }

  async makeMCPToolCall(serverName, toolName, args) {
    // This would be replaced with actual MCP protocol communication logic
    // Currently used by ExternalMCPClient subclasses if implemented
    throw new Error(`Real MCP tool call not implemented for external server ${serverName}`);
  }
}

// MCP Client Class - Proper MCP protocol implementation
class MCPClient {
  constructor(serverName = 'adn') {
    this.serverName = serverName;
    this.process = null;
    this.initialized = false;
    this.capabilities = null;
    this.tools = [];
    this.prompts = [];
    this.stdoutBuffer = '';
    this.pendingRequests = new Map();
  }

  // Start MCP server process
  async startServer() {
    return new Promise((resolve, reject) => {
      const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
      const scriptPath = path.join(REPO_ROOT, 'src', 'advanced_memory', 'mcp', 'server.py');

      addLog('INFO', `Starting ADN MCP server process...`, this.serverName);

      addLog('DEBUG', `Running: ${pythonPath} "${scriptPath}"`, this.serverName);
      addLog('DEBUG', `Working directory: ${REPO_ROOT}`, this.serverName);
      addLog('DEBUG', `PYTHONPATH: ${path.join(REPO_ROOT, 'src')}`, this.serverName);
      addLog('DEBUG', `Script exists: ${require('fs').existsSync(scriptPath)}`, this.serverName);

      // Check if Python is available
      const checkPython = spawn(pythonPath, ['--version'], { stdio: 'pipe' });
      checkPython.on('close', (code) => {
        if (code !== 0) {
          addLog('ERROR', `Python not available at ${pythonPath}`, this.serverName);
          reject(new Error(`Python not found at ${pythonPath}`));
          return;
        }

        addLog('INFO', 'Python is available, proceeding with MCP server startup...', this.serverName);

        // Start the actual ADN MCP server using the correct MCP protocol
        addLog('INFO', 'Starting actual ADN MCP server process...', this.serverName);

        // Set up environment for MCP server
        const env = {
          ...process.env,
          PYTHONPATH: path.join(REPO_ROOT, 'src'),
          PYTHONUNBUFFERED: '1',
          MCP_STDIO_MODE: 'true'  // Ensure MCP stdio mode
        };

        // Spawn the MCP server process with correct arguments
        this.process = spawn(pythonPath, ['-m', 'advanced_memory.mcp.server'], {
          cwd: REPO_ROOT,
          env: env,
          stdio: ['pipe', 'pipe', 'pipe'] // stdin, stdout, stderr
        });

        addLog('INFO', `ADN MCP server process started with PID: ${this.process.pid}`, this.serverName);

        this.stdoutBuffer = '';
        let stderrBuffer = '';

        // Handle stdout (MCP protocol messages)
        this.process.stdout.on('data', (data) => {
          const chunk = data.toString();
          addLog('DEBUG', `RAW STDOUT: ${chunk.substring(0, 100)}${chunk.length > 100 ? '...' : ''}`, this.serverName);
          this.stdoutBuffer += chunk;
          this.stdoutBuffer = this._processMCPMessages(this.stdoutBuffer);
        });

        // Handle stderr
        this.process.stderr.on('data', (data) => {
          const stderr = data.toString();
          addLog('DEBUG', stderr.trim(), this.serverName);
          stderrBuffer += stderr;

          // Check for initialization success indicators
          if (stderr.includes('FastMCP') || stderr.includes('server') || stderr.includes('started')) {
            addLog('INFO', 'ADN MCP server initializing...', this.serverName);
          }
        });

        // Handle process exit
        this.process.on('exit', (code, signal) => {
          addLog('INFO', `ADN MCP server process exited with code ${code}, signal ${signal}`, this.serverName);
          this.initialized = false;
          if (code !== 0 && code !== null) {
            addLog('ERROR', `ADN MCP server failed with exit code ${code}`, this.serverName);
          }
        });

        // Handle process errors
        this.process.on('error', (error) => {
          addLog('ERROR', `Failed to start ADN MCP server process: ${error.message}`, this.serverName);
          reject(error);
        });

        // Initialize MCP connection after process starts
        setTimeout(async () => {
          try {
            addLog('INFO', 'Attempting MCP initialization...', this.serverName);
            await this.initialize();
            addLog('INFO', 'ADN MCP server successfully initialized via MCP protocol', this.serverName);
            resolve(this);
          } catch (error) {
            addLog('ERROR', `MCP initialization failed: ${error.message}`, this.serverName);
            reject(error);
          }
        }, 2000); // Wait 2 seconds for process to start
      });
    });
  }

  // Process incoming MCP messages from stdout
  _processMCPMessages(buffer) {
    // Parse MCP protocol messages (Supports both Content-Length prefixed and raw JSON per line)
    let remainingBuffer = buffer;

    while (remainingBuffer.length > 0) {
      remainingBuffer = remainingBuffer.trimStart();
      if (remainingBuffer.length === 0) break;

      // Case 1: Header-based message (Content-Length: 123\r\n\r\n{...})
      if (remainingBuffer.startsWith('Content-Length:')) {
        const headerEndIndex = remainingBuffer.indexOf('\r\n\r\n');
        if (headerEndIndex === -1) break; // Wait for complete header

        const headers = remainingBuffer.substring(0, headerEndIndex);
        const contentLengthMatch = headers.match(/Content-Length:\s*(\d+)/i);

        if (!contentLengthMatch) {
          addLog('ERROR', 'Invalid MCP message: no Content-Length header despite header start', this.serverName);
          // Skip this "header" to avoid getting stuck
          remainingBuffer = remainingBuffer.substring(headerEndIndex + 4);
          continue;
        }

        const contentLength = parseInt(contentLengthMatch[1]);
        const bodyStart = headerEndIndex + 4;
        const totalMessageLength = bodyStart + contentLength;

        if (remainingBuffer.length < totalMessageLength) break; // Wait for complete body

        const messageJson = remainingBuffer.substring(bodyStart, totalMessageLength);
        remainingBuffer = remainingBuffer.substring(totalMessageLength);

        try {
          const message = JSON.parse(messageJson);
          this._handleMCPMessage(message);
        } catch (error) {
          addLog('ERROR', `Failed to parse header-based MCP message: ${error.message}`, this.serverName);
        }
      }
      // Case 2: Raw JSON-RPC message (one per line or just the block)
      else if (remainingBuffer.startsWith('{')) {
        // Most stdio MCP servers send one JSON-RPC message per line
        const newlineIndex = remainingBuffer.indexOf('\n');

        if (newlineIndex === -1) {
          // If no newline, check if we might have a full JSON object at the end of buffer
          // For simplicity and robustness with FastMCP, we usually expect a newline
          break;
        }

        const messageJson = remainingBuffer.substring(0, newlineIndex).trim();
        remainingBuffer = remainingBuffer.substring(newlineIndex + 1);

        if (messageJson.length > 0) {
          try {
            const message = JSON.parse(messageJson);
            this._handleMCPMessage(message);
          } catch (error) {
            // If parsing fails, it might be a partial JSON or interleaved data
            // We'll keep it in the buffer if it doesn't look like a full message
            // But if it has a newline, it SHOULD be a full message in stdio
            addLog('DEBUG', `Failed to parse raw MCP line: ${error.message}. Line: ${messageJson.substring(0, 100)}...`, this.serverName);
          }
        }
      }
      else {
        // Garbage or interleaved stderr output that leaked to stdout
        const newlineIndex = remainingBuffer.indexOf('\n');
        if (newlineIndex !== -1) {
          const garbage = remainingBuffer.substring(0, newlineIndex).trim();
          if (garbage.length > 0) {
            addLog('DEBUG', `Skipping non-MCP stdout data: ${garbage.substring(0, 50)}...`, this.serverName);
          }
          remainingBuffer = remainingBuffer.substring(newlineIndex + 1);
        } else {
          // If no newline, wait or clear if buffer gets too large
          if (remainingBuffer.length > 4096) {
            addLog('WARN', 'Clearing large garbage buffer in stdout', this.serverName);
            remainingBuffer = '';
          }
          break;
        }
      }
    }

    return remainingBuffer;
  }

  // Handle incoming MCP messages
  _handleMCPMessage(message) {
    if (message.id && this.pendingRequests.has(message.id)) {
      // This is a response to a request we sent
      const pending = this.pendingRequests.get(message.id);
      this.pendingRequests.delete(message.id);
      clearTimeout(pending.timeout); // Clear the timeout

      if (message.error) {
        addLog('ERROR', `MCP error response for request ${message.id}: ${JSON.stringify(message.error)}`, this.serverName);
        pending.reject(new Error(`MCP Error: ${message.error.message}`));
      } else {
        addLog('DEBUG', `MCP success response for request: ${message.id}`, this.serverName);
        pending.resolve(message.result);
      }
    } else if (message.method) {
      // This is a server notification/request (not common in stdio mode)
      addLog('INFO', `Received MCP notification: ${message.method}`, this.serverName);
    } else {
      addLog('WARN', `Received unknown MCP message: ${JSON.stringify(message)}`, this.serverName);
    }
  }

  // Send MCP request
  async sendRequest(method, params = {}) {
    return new Promise((resolve, reject) => {
      if (!this.process || !this.process.stdin || this.process.stdin.writableEnded) {
        return reject(new Error('ADN MCP server process not running or stdin not writable'));
      }

      const requestId = nextRequestId++;
      addLog('DEBUG', `Sending MCP request: ${method} with id ${requestId}`, this.serverName);

      const request = {
        jsonrpc: '2.0',
        id: requestId,
        method: method,
        params: params
      };

      const timeout = setTimeout(() => {
        if (this.pendingRequests.has(requestId)) {
          this.pendingRequests.delete(requestId);
          addLog('ERROR', `MCP request timeout: ${method} (id: ${requestId})`, this.serverName);
          reject(new Error(`MCP request timeout: ${method}`));
        }
      }, 30000); // 30 seconds timeout

      this.pendingRequests.set(requestId, { resolve, reject, timeout });

      try {
        const requestJson = JSON.stringify(request);
        // Pure stdio MCP protocol usually doesn't use Content-Length headers
        // We send raw JSON string followed by a newline
        const message = `${requestJson}\n`;

        addLog('DEBUG', `Writing MCP message to stdin (id: ${requestId}): ${requestJson.substring(0, 200)}...`, this.serverName);
        this.process.stdin.write(message);
      } catch (error) {
        if (this.pendingRequests.has(requestId)) {
          clearTimeout(timeout);
          this.pendingRequests.delete(requestId);
        }
        addLog('ERROR', `Failed to send MCP request (id: ${requestId}): ${error.message}`, this.serverName);
        reject(error);
      }
    });
  }

  // Shutdown the MCP server
  async shutdown() {
    if (this.process) {
      addLog('INFO', `Shutting down ADN MCP server process (PID: ${this.process.pid})...`, this.serverName);
      this.process.kill('SIGTERM');

      // Give it time to shut down gracefully
      setTimeout(() => {
        if (this.process && !this.process.killed) {
          addLog('WARN', `Force killing ADN MCP server process (PID: ${this.process.pid})...`, this.serverName);
          this.process.kill('SIGKILL');
        }
      }, 5000);
    }
    this.initialized = false;
    this.capabilities = null;
    this.tools = [];
    this.prompts = [];
  }

  // Initialize MCP connection using proper protocol
  async initialize() {
    addLog('INFO', 'Initializing MCP connection...', this.serverName);

    try {
      addLog('INFO', 'Sending initialize request...', this.serverName);
      const result = await this.sendRequest('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: {
          tools: {},
          prompts: {}
        },
        clientInfo: {
          name: 'ADN Web Bridge',
          version: '1.0.0'
        }
      });

      addLog('DEBUG', `MCP initialize result: ${JSON.stringify(result, null, 2)}`, this.serverName);
      this.capabilities = result.capabilities || {};
      this.initialized = true;

      addLog('INFO', 'Sending initialized notification...', this.serverName);
      // Notifications have no id and no response
      try {
        const notif = { jsonrpc: '2.0', method: 'notifications/initialized' };
        const body = JSON.stringify(notif);
        this.process.stdin.write(`${body}\n`);
        addLog('INFO', 'Initialized notification sent', this.serverName);
      } catch (err) {
        addLog('WARN', `Initialized notification send error (non-fatal): ${err.message}`, this.serverName);
      }

      // Discover available tools and prompts
      addLog('INFO', 'Discovering capabilities...', this.serverName);
      await this.discoverCapabilities();
      addLog('INFO', 'Capabilities discovered successfully', this.serverName);

    } catch (error) {
      addLog('ERROR', `MCP initialization failed: ${error.message}`, this.serverName);
      throw error;
    }
  }

  // Discover server capabilities
  async discoverCapabilities() {
    addLog('INFO', 'Discovering MCP capabilities...', this.serverName);

    try {
      // Get available tools
      const toolsResult = await this.sendRequest('tools/list');
      this.tools = toolsResult.tools || [];
      addLog('INFO', `Discovered ${this.tools.length} MCP tools: ${this.tools.map(t => t.name).join(', ')}`, this.serverName);

      // Get available prompts
      const promptsResult = await this.sendRequest('prompts/list');
      this.prompts = promptsResult.prompts || [];
      addLog('INFO', `Discovered ${this.prompts.length} MCP prompts: ${this.prompts.map(p => p.name).join(', ')}`, this.serverName);

    } catch (error) {
      addLog('ERROR', `Failed to discover capabilities: ${error.message}`, this.serverName);
      // Continue anyway - some servers might not support discovery
    }
  }

  // Call a tool using proper MCP protocol
  async callTool(name, args = {}) {
    addLog('INFO', `Calling tool: ${name}`, this.serverName);

    try {
      // Use the proper MCP tools/call method
      const result = await this.sendRequest('tools/call', {
        name: name,
        arguments: args
      });
      return result;
    } catch (error) {
      addLog('ERROR', `Tool call failed: ${name} - ${error.message}`, this.serverName);
      throw error;
    }
  }

  // No simulation fallback
  async getPrompt(name, args = {}) {
    addLog('INFO', `Getting prompt: ${name}`, this.serverName);
    return await this.sendRequest('prompts/get', {
      name: name,
      arguments: args
    });
  }

  // Shutdown the MCP server
  shutdown() {
    if (this.process) {
      addLog('INFO', `Shutting down MCP server process (PID: ${this.process.pid})`, this.serverName);
      this.process.kill();
      this.process = null;
    }
    this.initialized = false;
    this.capabilities = null;
    this.tools = [];
    this.prompts = [];
  }
}

// Initialize ADN MCP server process (local) - now async and non-blocking
function startMCPProcess() {
  return new Promise(async (resolve, reject) => {
    try {
      addLog('INFO', 'Creating ADN MCP client...', 'bridge');
      const client = new MCPClient();

      // Start server asynchronously
      client.startServer().then(() => {
        mcpClients.set('adn', client);
        addLog('SUCCESS', 'ADN MCP client fully initialized with tools and prompts', 'bridge');
        addLog('INFO', `ADN client has ${client.tools ? client.tools.length : 0} tools and ${client.prompts ? client.prompts.length : 0} prompts`, 'bridge');
        resolve(client);
      }).catch((error) => {
        addLog('ERROR', `Failed to start ADN MCP client: ${error.message}`, 'bridge');
        reject(error);
      });

    } catch (error) {
      addLog('ERROR', `Failed to create ADN MCP client: ${error.message}`, 'bridge');
      reject(error);
    }
  });
}

// Initialize external MCP server connections
async function initializeExternalMCPServers() {
  const externalServers = [
    { name: 'brightdata', description: 'BrightData web scraping service' },
    { name: 'fetch', description: 'HTTP fetch client' }
    // Add more external servers here as needed
  ];

  console.log('Initializing external MCP server connections...');

  for (const server of externalServers) {
    try {
      console.log(`Creating external MCP client for ${server.name}...`);
      const client = new ExternalMCPClient(server.name);
      // Initialize asynchronously without waiting - this prevents blocking the server startup
      client.initialize().then(() => {
        console.log(`External MCP server '${server.name}' initialized successfully`);
      }).catch((error) => {
        console.error(`Failed to initialize external MCP server '${server.name}':`, error);
        console.log(`'${server.name}' will use fallback simulation mode`);
      });

      // Set the client immediately - it will work in simulation mode until properly initialized
      mcpClients.set(server.name, client);
      console.log(`External MCP client '${server.name}' registered (initializing in background)`);
    } catch (error) {
      console.error(`Failed to create external MCP client for '${server.name}':`, error);
      // Create a basic client that can still respond to requests
      const fallbackClient = new ExternalMCPClient(server.name);
      fallbackClient.initialized = false; // Mark as not fully initialized but available
      mcpClients.set(server.name, fallbackClient);
      console.log(`Created fallback client for '${server.name}'`);
    }
  }
}

// Unwrap MCP tools/call result: server may return { content: [ { type: "text", text: "<json>" } ] }
function unwrapMCPToolResult(mcpResult) {
  if (!mcpResult) return mcpResult;
  const first = mcpResult.content && mcpResult.content[0];
  if (first && typeof first.text === 'string') {
    try {
      return JSON.parse(first.text);
    } catch (e) {
      // If NOT JSON, return the raw text instead of the whole result object
      // This ensures we ingest raw markdown/html correctly in the bridge
      console.log('DEBUG: unwrapMCPToolResult ingested raw text content');
      return first.text;
    }
  }
  return mcpResult;
}

// MCP communication helper - uses proper MCP client
async function sendMCPRequest(toolName, params = {}) {
  const adnClient = mcpClients.get('adn');
  if (!adnClient || !adnClient.initialized) {
    throw new Error('ADN MCP client not initialized');
  }

  addLog('INFO', `Calling ADN MCP tool: ${toolName}`, 'bridge');
  return await adnClient.callTool(toolName, params);
}

// Removed mock responses - now using real MCP communication

// API Routes

// Test route to verify Express is working
app.get('/test', (req, res) => {
  addLog('INFO', `Test route called from: ${req.ip}`, 'bridge');
  res.json({ status: 'ok', message: 'Express server is working', timestamp: new Date().toISOString() });
});

// Lightweight health for webapp (no MCP init). Webapp checks this to detect bridge up.
app.get('/api/v1/health', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.status(200).json({
    status: 'ok',
    bridge: 'running',
    mcp_connected: mcpClients.has('adn') && mcpClients.get('adn').initialized,
    timestamp: new Date().toISOString()
  });
});

app.get('/health', async (req, res) => {
  console.log('Health endpoint called');

  try {
    // Ensure ADN MCP is initialized if not already
    await ensureMCPInitialized();

    // Wait a bit for ADN initialization to complete
    if (!mcpClients.has('adn')) {
      console.log('Waiting for ADN MCP initialization...');
      await new Promise(resolve => setTimeout(resolve, 2000));
    }

    const servers = {};
    for (const [name, client] of mcpClients) {
      servers[name] = {
        initialized: client.initialized,
        tools: client.tools ? client.tools.length : 0,
        prompts: client.prompts ? client.prompts.length : 0
      };
    }

    const response = {
      status: 'ok',
      bridge: 'running',
      servers: servers,
      total_servers: mcpClients.size,
      timestamp: new Date().toISOString()
    };

    console.log('Health response data:', JSON.stringify(response, null, 2));

    // Send response
    res.setHeader('Content-Type', 'application/json');
    res.status(200).json(response);

    console.log('Health response sent successfully');
  } catch (error) {
    console.error('Health endpoint error:', error);
    res.status(500).json({
      status: 'error',
      message: 'Health check failed',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// MCP Capabilities endpoints
app.get('/api/v1/mcp/tools', async (req, res) => {
  try {
    const adnClient = mcpClients.get('adn');
    if (!adnClient || !adnClient.initialized) {
      return res.status(503).json({ success: false, error: 'ADN MCP client not initialized' });
    }

    res.json({
      success: true,
      data: {
        tools: adnClient.tools,
        count: adnClient.tools.length
      }
    });
  } catch (error) {
    console.error('MCP tools API error:', error);
    res.status(500).json({ success: false, error: 'Failed to get MCP tools' });
  }
});

app.get('/api/v1/mcp/prompts', async (req, res) => {
  try {
    const adnClient = mcpClients.get('adn');
    if (!adnClient || !adnClient.initialized) {
      return res.status(503).json({ success: false, error: 'ADN MCP client not initialized' });
    }

    res.json({
      success: true,
      data: {
        prompts: adnClient.prompts,
        count: adnClient.prompts.length
      }
    });
  } catch (error) {
    console.error('MCP prompts API error:', error);
    res.status(500).json({ success: false, error: 'Failed to get MCP prompts' });
  }
});

app.post('/api/v1/mcp/tools/:toolName', async (req, res) => {
  try {
    const adnClient = mcpClients.get('adn');
    if (!adnClient || !adnClient.initialized) {
      return res.status(503).json({ success: false, error: 'ADN MCP client not initialized' });
    }

    const { toolName } = req.params;
    const args = req.body.arguments || {};

    console.log(`Calling ADN MCP tool via API: ${toolName}`, args);
    const result = await adnClient.callTool(toolName, args);
    const payload = unwrapMCPToolResult(result);

    res.json({
      success: true,
      data: payload
    });
  } catch (error) {
    console.error('MCP tool call API error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/v1/mcp/prompts/:promptName', async (req, res) => {
  try {
    const adnClient = mcpClients.get('adn');
    if (!adnClient || !adnClient.initialized) {
      return res.status(503).json({ success: false, error: 'ADN MCP client not initialized' });
    }

    const { promptName } = req.params;
    const args = req.body.arguments || {};

    console.log(`Getting ADN MCP prompt via API: ${promptName}`, args);
    const result = await adnClient.getPrompt(promptName, args);

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('MCP prompt API error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// External MCP Server Routes - BrightData and Fetch

// BrightData routes
app.post('/api/v1/brightdata/search', async (req, res) => {
  try {
    const { query, options = {} } = req.body;
    console.log('BrightData search request:', { query, options });

    const client = mcpClients.get('brightdata');
    if (!client) {
      return res.status(503).json({ success: false, error: 'BrightData MCP server not initialized' });
    }

    const result = await client.callTool('search_engine', { query, ...options });

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('BrightData search error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

app.post('/api/v1/brightdata/scrape', async (req, res) => {
  try {
    const { url, options = {} } = req.body;
    console.log('BrightData scrape request:', { url, options });

    const client = mcpClients.get('brightdata');
    if (!client) {
      return res.status(503).json({ success: false, error: 'BrightData MCP server not initialized' });
    }

    const result = await client.callTool('scrape_as_markdown', { url, ...options });

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('BrightData scrape error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Fetch routes
app.post('/api/v1/fetch', async (req, res) => {
  try {
    const { url, method = 'GET', headers = {}, body } = req.body;
    console.log('Fetch request:', { url, method, headers: Object.keys(headers), body: body ? 'present' : 'none' });

    const client = mcpClients.get('fetch');
    if (!client) {
      return res.status(503).json({ success: false, error: 'Fetch MCP server not initialized' });
    }

    const result = await client.callTool('fetch', { url, method, headers, body });

    res.json({
      success: true,
      data: result
    });
  } catch (error) {
    console.error('Fetch error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Generic external MCP server proxy
app.post('/api/v1/mcp/external/:server/:tool', async (req, res) => {
  try {
    await ensureMCPInitialized();

    const { server, tool } = req.params;
    const args = req.body.arguments || req.body || {};

    console.log(`External MCP request: ${server}/${tool}`, args);

    // Get the appropriate MCP client
    const client = mcpClients.get(server);
    if (!client || !client.initialized) {
      return res.status(503).json({
        success: false,
        error: `MCP server '${server}' not available or not initialized`
      });
    }

    // Call the tool
    const result = await client.callTool(tool, args);

    res.json({
      success: true,
      data: {
        server: server,
        tool: tool,
        result: result
      }
    });
  } catch (error) {
    console.error('External MCP error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Notes routes - now using real MCP communication
const MCP_INIT_TIMEOUT_MS = 20000;

app.get('/api/v1/notes', async (req, res) => {
  try {
    const timeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('MCP init timeout')), MCP_INIT_TIMEOUT_MS)
    );
    try {
      await Promise.race([ensureMCPInitialized(), timeout]);
    } catch (e) {
      if (e && e.message === 'MCP init timeout') {
        console.warn('Notes: MCP init timeout, returning empty notes');
        return res.json({
          success: true,
          data: { notes: [], total: 0, page: 1, pages: 1 }
        });
      }
      throw e;
    }

    const query = (req.query.query || '').trim();
    const page = parseInt(req.query.page) || 1;
    const pageSize = parseInt(req.query.limit) || 50;

    // For empty query: use recent_activity to list notes (adn_search returns nothing for empty query)
    let rawResults = [];
    let resultMeta = { total_results: 0, current_page: page, total_pages: 1, page_size: pageSize };

    if (!query) {
      console.log('Fetching all notes via wildcard search...', { page, page_size: pageSize });
      const searchResponse = await sendMCPRequest('adn_knowledge', {
        operation: 'search',
        query: '*',
        search_type: 'permalink',
        entity_type: 'entity',
        page,
        results_per_page: pageSize
      });
      const payload = unwrapMCPToolResult(searchResponse);
      const results = payload?.result?.results || payload?.technical_summary?.results || [];
      rawResults = results;
      resultMeta = {
        total_results: payload?.result?.total_results || payload?.technical_summary?.total_results || results.length,
        current_page: page,
        total_pages: Math.ceil((payload?.result?.total_results || results.length) / pageSize),
        page_size: pageSize
      };
    } else {
      console.log('Searching notes...', { query, page, page_size: pageSize });
      const mcpResponse = await sendMCPRequest('adn_knowledge', {
        operation: 'search',
        query,
        entity_type: 'entity',
        page,
        results_per_page: pageSize
      });
      const payload = unwrapMCPToolResult(mcpResponse);
      rawResults = payload?.result?.results || payload?.results || [];
      resultMeta = {
        total_results: payload?.result?.total_results || rawResults.length,
        current_page: page,
        total_pages: Math.ceil((payload?.result?.total_results || rawResults.length) / pageSize),
        page_size: pageSize
      };
    }

    console.log('MCP notes response:', rawResults.length, 'items');

    const total = resultMeta.total_results;
    const totalPages = resultMeta.total_pages;
    const currentPage = resultMeta.current_page;

    const notes = [];
    if (Array.isArray(rawResults)) {
      rawResults.forEach((item) => {
        if (item && typeof item === 'object') {
          const permalink = item.permalink || item.id;
          notes.push({
            id: permalink || item.title?.toLowerCase?.()?.replace(/\s+/g, '-') || `note-${notes.length}`,
            title: item.title || 'Untitled',
            content: item.content_preview || item.content || item.summary || '',
            tags: Array.isArray(item.tags) ? item.tags : [],
            created: item.created_at || item.created || item.date || new Date().toISOString(),
            modified: item.updated_at || item.modified || item.updated || new Date().toISOString(),
            wordCount: item.wordCount ?? (item.content_preview ? item.content_preview.split(/\s+/).length : 0),
            connections: item.connections ?? 0,
            permalink
          });
        }
      });
    }

    res.json({
      success: true,
      data: {
        notes,
        total,
        page: currentPage,
        pages: totalPages
      }
    });
  } catch (error) {
    console.error('Notes API error:', error);
    // Return empty results instead of crashing
    res.json({
      success: true,
      data: { notes: [], total: 0, page: 1, pages: 1 }
    });
  }
});

// --- Note Graph (PointCloud) Route ---
app.get('/api/v1/notes/graph', async (req, res) => {
  try {
    // Get all notes via knowledge tool
    const result = await sendMCPRequest('adn_knowledge', {
      operation: 'search',
      query: '',
      entity_type: 'entity',
      page_size: 100
    });
    const payload = unwrapMCPToolResult(result);

    // Structure for graph (nodes and links)
    const nodes = [];
    const links = [];
    const nodeSet = new Set();

    // Traverse results prioritizing the structured payload
    const items = payload?.result?.results || payload?.technical_summary?.results || payload?.result || payload?.results || [];

    for (const item of items) {
      const id = item.permalink || item.id || item.title;
      if (id && !nodeSet.has(id)) {
        nodes.push({
          id,
          label: item.title || id,
          type: item.type || 'note'
        });
        nodeSet.add(id);
      }

      // Add edges if links exist
      if (Array.isArray(item.links)) {
        item.links.forEach(target => {
          links.push({ source: id, target, type: 'link' });
        });
      }
    }

    res.json({ success: true, data: { nodes, links } });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Use param to capture permalinks with slashes (e.g. specs/search-spec)
app.get('/api/v1/notes/:path(.*)', async (req, res) => {
  const noteId = req.params.path || req.path.replace(/^\/api\/v1\/notes\/?/, '') || '';
  if (!noteId) {
    return res.status(400).json({ success: false, error: 'Note ID required' });
  }
  try {
    const timeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('MCP init timeout')), MCP_INIT_TIMEOUT_MS)
    );
    try {
      await Promise.race([ensureMCPInitialized(), timeout]);
    } catch (e) {
      if (e && e.message === 'MCP init timeout') {
        return res.status(503).json({ success: false, error: 'MCP initializing' });
      }
      throw e;
    }

    console.log(`Fetching note ${noteId} via MCP...`);
    const mcpResponse = await sendMCPRequest('adn_content', {
      operation: 'read',
      identifier: noteId
    });
    const payload = unwrapMCPToolResult(mcpResponse);

    console.log('MCP content response:', payload ? (typeof payload === 'string' ? 'string' : 'object') : 'null');

    // Handle structured error responses
    if (payload && typeof payload === 'object' && payload.success === false) {
      console.warn('DEBUG: adn_content returned error payload:', payload.error);
      return res.status(404).json({
        success: false,
        error: payload.message || payload.error,
        recovery: payload.recovery_options
      });
    }

    // Detect MCP conversational "not found" response so we don't return it as note content
    const contentStr = typeof payload === 'string' ? payload : (payload?.result?.content ?? payload?.result?.text ?? payload?.technical_summary?.content ?? payload?.content ?? payload?.text ?? '');
    const isNotFoundResponse = typeof contentStr === 'string' && (
      /#\s*Note Not Found:/i.test(contentStr) ||
      /couldn't find an exact match/i.test(contentStr) ||
      /I searched for .* but couldn't find/i.test(contentStr) ||
      /read_note\s*\(\s*["']/i.test(contentStr) && /consider creating a new note/i.test(contentStr)
    );
    if (isNotFoundResponse) {
      console.warn('adn_content returned conversational not-found response for identifier:', noteId);
      return res.status(404).json({ success: false, error: 'Note not found' });
    }

    // adn_content read returns either: (a) raw markdown string, or (b) build_success_response dict with result
    let noteData = null;
    if (typeof payload === 'string' && payload.length > 0) {
      // Raw markdown - extract title from first # heading
      const titleMatch = payload.match(/^#\s+(.+)$/m);
      noteData = {
        id: noteId,
        title: titleMatch ? titleMatch[1].trim() : noteId.replace(/-/g, ' '),
        content: payload,
        tags: [],
        created: new Date().toISOString(),
        modified: new Date().toISOString(),
        wordCount: payload.split(/\s+/).filter(Boolean).length,
        connections: 0,
        permalink: noteId
      };
    } else if (payload && typeof payload === 'object') {
      // Extract data from the result field if it exists (standard wrap) or use payload directly
      const r = payload.result || payload.technical_summary || payload;

      const content = r.content || r.text || (typeof r === 'string' ? r : '');

      noteData = {
        id: r.id || r.permalink || noteId,
        title: r.title || 'Untitled',
        content: content,
        tags: Array.isArray(r.tags) ? r.tags : [],
        created: r.created || r.date || new Date().toISOString(),
        modified: r.modified || r.updated || new Date().toISOString(),
        wordCount: r.wordCount ?? (typeof content === 'string' ? content.split(/\s+/).filter(Boolean).length : 0),
        connections: r.connections ?? 0,
        permalink: r.permalink || r.id || noteId
      };
    }

    if (noteData) {
      res.json({ success: true, data: noteData });
    } else {
      res.status(404).json({ success: false, error: 'Note not found' });
    }
  } catch (error) {
    console.error('Note API error:', error);
    res.status(500).json({ success: false, error: 'Failed to fetch note' });
  }
});

// Skills routes - scan actual IDE directories
app.get('/api/v1/skills', async (req, res) => {
  try {
    const { folder } = req.query;
    const skills = [];
    const folders = ['cursor-skills', 'windsurf-skills', 'adn-skills', 'antigravity-skills'];

    console.log('Skills API called with folder:', folder);

    if (folder) {
      // Scan specific folder for skills
      console.log('Scanning specific folder:', folder);
      const skillDir = getSkillDirectory(folder);
      console.log('Skill directory path:', skillDir);
      if (skillDir) {
        const folderSkills = await scanSkillDirectory(skillDir, folder);
        console.log(`Found ${folderSkills.length} skills in ${folder}`);
        skills.push(...folderSkills);
      } else {
        console.log('Could not determine skill directory for:', folder);
      }
    } else {
      // Scan all folders
      console.log('Scanning all folders');
      for (const folderName of folders) {
        console.log('Checking folder:', folderName);
        const skillDir = getSkillDirectory(folderName);
        console.log('Skill directory path:', skillDir);
        if (skillDir) {
          try {
            const folderSkills = await scanSkillDirectory(skillDir, folderName);
            console.log(`Found ${folderSkills.length} skills in ${folderName}`);
            skills.push(...folderSkills);
          } catch (scanError) {
            console.log(`Error scanning ${folderName}:`, scanError.message);
          }
        } else {
          console.log(`Could not determine skill directory for ${folderName}`);
        }
      }
    }

    console.log(`Total skills found: ${skills.length}`);

    res.json({
      success: true,
      data: {
        skills: skills,
        folders: folders
      }
    });
  } catch (error) {
    console.error('Skills API error:', error);
    res.json({
      success: true,
      data: {
        skills: [],
        folders: ['cursor-skills', 'windsurf-skills', 'adn-skills', 'antigravity-skills']
      }
    });
  }
});

// Initialize MCP servers on first request
async function ensureMCPInitialized() {
  console.log('ensureMCPInitialized called. Current MCP clients:', Array.from(mcpClients.keys()));

  // Initialize external MCP servers first (they're more reliable)
  if (!mcpClients.has('brightdata') || !mcpClients.has('fetch')) {
    console.log('Initializing external MCP clients...');
    initializeExternalMCPServers(); // Don't await - run in background
  }

  // Initialize ADN server asynchronously (don't block server startup)
  if (!mcpClients.has('adn')) {
    console.log('Starting ADN MCP client initialization...');
    try {
      await startMCPProcess();
      console.log('ADN MCP client initialized successfully');
    } catch (error) {
      console.error('Failed to initialize ADN MCP client:', error);
      console.log('Continuing without ADN MCP client - external MCP servers still available');
    }
  } else {
    console.log('ADN MCP client already exists');
  }

  console.log('ensureMCPInitialized completed. Final MCP clients:', Array.from(mcpClients.keys()));
}

// Start server
async function startServer() {
  console.log('Starting ADN MCP Bridge Server...');

  // Initialize external MCP servers immediately on startup
  console.log('Initializing external MCP servers on startup...');
  await initializeExternalMCPServers();

  // Log that routes should be registered
  console.log('Routes should be registered now');

  // Start HTTP server - bind to all interfaces for Tailnet access
  // --- Projects Routes ---
  app.get('/api/v1/projects', async (req, res) => {
    console.log('DEBUG: GET /api/v1/projects route hit');
    try {
      const result = await sendMCPRequest('adn_project', { operation: 'list' });
      const payload = unwrapMCPToolResult(result);
      console.log('DEBUG: projects payload keys:', payload ? Object.keys(payload) : 'null');
      console.log('DEBUG: payload.result type:', typeof payload?.result);
      // Prioritize 'result' which now carries raw data, fallback to technical_summary for compatibility
      const projects = payload?.result || payload?.technical_summary || [];
      console.log('DEBUG: sending projects:', Array.isArray(projects) ? `Array(${projects.length})` : typeof projects);
      res.json({ success: true, data: projects });
    } catch (error) {
      console.error('DEBUG: projects route error:', error.message);
      res.status(500).json({ success: false, error: error.message });
    }
  });

  app.post('/api/v1/projects', async (req, res) => {
    try {
      const { name, path: projectPath, description, set_default } = req.body;
      const result = await sendMCPRequest('adn_project', {
        operation: 'create',
        project_name: name,
        project_path: projectPath,
        set_default
      });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, data: payload?.result || payload?.technical_summary || payload });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  app.post('/api/v1/projects/switch', async (req, res) => {
    try {
      const { name } = req.body;
      const result = await sendMCPRequest('adn_project', { operation: 'switch', project_name: name });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, data: payload?.result || payload?.technical_summary || payload });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  app.delete('/api/v1/projects/:name', async (req, res) => {
    try {
      const { name } = req.params;
      const result = await sendMCPRequest('adn_project', { operation: 'delete', project_name: name });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, data: payload?.result || payload?.technical_summary || payload });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // --- Batch Import Routes ---
  const fs = require('fs').promises;
  const path = require('path');
  const fsNative = require('fs');

  async function scanDirRecursive(dir, minDate) {
    let results = [];
    const list = await fs.readdir(dir);
    for (const file of list) {
      const filePath = path.join(dir, file);
      const stat = await fs.stat(filePath);
      if (stat.isDirectory()) {
        results = results.concat(await scanDirRecursive(filePath, minDate));
      } else if (path.extname(file).toLowerCase() === '.md') {
        if (!minDate || stat.mtime >= minDate) {
          results.push({
            name: file,
            path: filePath,
            size: stat.size,
            modified: stat.mtime
          });
        }
      }
    }
    return results;
  }

  app.post('/api/v1/import/scan', async (req, res) => {
    try {
      const { path: scanPath, months = 0 } = req.body;
      if (!scanPath) throw new Error('Path required for scan');

      let minDate = null;
      if (months > 0) {
        minDate = new Date();
        minDate.setMonth(minDate.getMonth() - months);
      }

      const files = await scanDirRecursive(scanPath, minDate);
      res.json({ success: true, data: files });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  app.post('/api/v1/import/batch', async (req, res) => {
    try {
      const { files, destination_folder, project } = req.body;
      const client = mcpClients.get('adn');
      if (!client) throw new Error('ADN MCP client not initialized');

      const results = [];
      for (const filePath of files) {
        try {
          const result = await client.callTool('adn_import', {
            operation: 'obsidian', // Generic MD import uses obsidian logic
            source_path: filePath,
            destination_folder,
            project
          });
          results.push({ path: filePath, success: true, result });
        } catch (e) {
          results.push({ path: filePath, success: false, error: e.message });
        }
      }

      res.json({ success: true, data: results });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // --- Skill Marketplace Routes (ClawHub + local ADN) ---
  const OPENCLAW_API = process.env.OPENCLAW_API_BASE || 'http://localhost:10765';

  // Fetch ClawHub / OpenClaw skills from openclaw-molt-mcp webapp_api
  app.get('/api/v1/marketplace/openclaw', async (req, res) => {
    try {
      const axios = require('axios');
      const response = await axios.get(`${OPENCLAW_API}/api/skills`, { timeout: 5000 });
      res.json({ success: true, source: 'openclaw', data: response.data });
    } catch (error) {
      res.json({ success: false, source: 'openclaw', error: error.message, data: { skills: [] } });
    }
  });

  // Fetch skill content from ClawHub
  app.get('/api/v1/marketplace/openclaw/:name', async (req, res) => {
    try {
      const axios = require('axios');
      const { name } = req.params;
      const response = await axios.get(`${OPENCLAW_API}/api/skills/${encodeURIComponent(name)}/content`, { timeout: 5000 });
      res.json({ success: true, source: 'openclaw', data: response.data });
    } catch (error) {
      res.status(error.response?.status || 500).json({ success: false, error: error.message });
    }
  });

  // Fetch ClawNews from openclaw-molt-mcp
  app.get('/api/v1/marketplace/clawnews', async (req, res) => {
    try {
      const axios = require('axios');
      const response = await axios.get(`${OPENCLAW_API}/api/clawnews`, { timeout: 5000 });
      res.json({ success: true, data: response.data });
    } catch (error) {
      res.json({ success: false, error: error.message, data: { items: [] } });
    }
  });

  // List local ADN skills
  app.get('/api/v1/marketplace/local', async (req, res) => {
    try {
      const result = await sendMCPRequest('adn_skills', { operation: 'list' });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, source: 'local', data: payload });
    } catch (error) {
      res.json({ success: false, source: 'local', error: error.message });
    }
  });

  // Search ADN skills
  app.get('/api/v1/marketplace/search', async (req, res) => {
    try {
      const { query } = req.query;
      const result = await sendMCPRequest('adn_skills', { operation: 'search', query: query || '' });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, data: payload });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Import / install a skill from ClawHub into ADN
  app.post('/api/v1/marketplace/import', async (req, res) => {
    try {
      const { skill_name, content } = req.body;
      const result = await sendMCPRequest('adn_skills', {
        operation: 'create',
        name: skill_name,
        content: content
      });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, data: payload });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // --- Research Lab Routes ---
  app.post('/api/v1/research/run', async (req, res) => {
    try {
      const { topic, sources, max_iterations, coverage_threshold } = req.body;
      const result = await sendMCPRequest('adn_research', {
        operation: 'web_search',
        query: topic
      });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, data: payload });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // --- Zettelkasten Routes ---

  // Get Inbox notes (files in Inbox folder)
  app.get('/api/v1/zettel/inbox', async (req, res) => {
    try {
      // Assuming 'Inbox' is a folder in the project root or specified path
      // Using adn_knowledge list operation
      const result = await sendMCPRequest('adn_knowledge', {
        operation: 'list',
        path: 'Inbox'
      });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, data: payload });
    } catch (error) {
      res.json({ success: false, error: error.message, data: [] });
    }
  });

  // Link two notes (Bidirectional or Unidirectional)
  app.post('/api/v1/zettel/link', async (req, res) => {
    try {
      const { source_id, target_id, type = 'bidirectional' } = req.body;

      // 1. Read source note to append link
      const sourceResult = await sendMCPRequest('adn_knowledge', { operation: 'read', identifier: source_id });
      let sourceContent = unwrapMCPToolResult(sourceResult)?.content || '';

      if (!sourceContent.includes(`[[${target_id}]]`)) {
        const newSourceContent = sourceContent + `\n\n[[${target_id}]]`;
        await sendMCPRequest('adn_knowledge', {
          operation: 'update',
          identifier: source_id,
          content: newSourceContent
        });
      }

      // 2. If bidirectional, read target note and append link to source
      if (type === 'bidirectional') {
        const targetResult = await sendMCPRequest('adn_knowledge', { operation: 'read', identifier: target_id });
        let targetContent = unwrapMCPToolResult(targetResult)?.content || '';

        if (!targetContent.includes(`[[${source_id}]]`)) {
          const newTargetContent = targetContent + `\n\n[[${source_id}]]`;
          await sendMCPRequest('adn_knowledge', {
            operation: 'update',
            identifier: target_id,
            content: newTargetContent
          });
        }
      }

      res.json({ success: true, message: `Linked ${source_id} <-> ${target_id}` });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Promote note from Inbox to Zettelkasten (Main)
  app.post('/api/v1/zettel/promote', async (req, res) => {
    try {
      const { identifier, destination = 'Zettelkasten' } = req.body;
      // Move the file
      const result = await sendMCPRequest('adn_knowledge', {
        operation: 'move',
        identifier: identifier,
        folder: destination
      });
      const payload = unwrapMCPToolResult(result);
      res.json({ success: true, data: payload });
    } catch (error) {
      res.status(500).json({ success: false, error: error.message });
    }
  });

  // Start the server
  const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`ADN MCP Bridge Server running on http://0.0.0.0:${PORT} (Tailnet accessible)`);
    addLog('INFO', 'External MCP servers initialized on startup. Initializing ADN MCP server...', 'bridge');

    // Initialize ADN MCP server immediately on startup
    startMCPProcess().then(() => {
      addLog('SUCCESS', 'ADN MCP server initialized successfully on startup', 'bridge');
    }).catch((error) => {
      addLog('ERROR', `Failed to initialize ADN MCP server on startup: ${error.message}`, 'bridge');
      addLog('WARNING', 'ADN MCP routes will not be available', 'bridge');
    });
  });

  // Handle server errors gracefully
  server.on('error', (error) => {
    console.error('HTTP server error:', error);
  });

  // Keep server alive - don't exit on ADN MCP failures
  process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
    // Don't exit - try to keep server running
  });

  process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled rejection at:', promise, 'reason:', reason);
    // Don't exit - try to keep server running
  });
}

// System and Logging Routes

app.get('/api/v1/system/logs', (req, res) => {
  const { limit = 100, source } = req.query;
  let filteredLogs = logBuffer;
  if (source) {
    filteredLogs = filteredLogs.filter(l => l.source === source);
  }
  res.json({
    success: true,
    data: filteredLogs.slice(-parseInt(limit))
  });
});

app.get('/api/v1/system/status', async (req, res) => {
  const mcpServers = {};
  for (const [name, client] of mcpClients) {
    mcpServers[name] = {
      initialized: client.initialized,
      tools: client.tools ? client.tools.length : 0,
      prompts: client.prompts ? client.prompts.length : 0
    };
  }

  let knowledgeStatus = {};
  try {
    const result = await sendMCPRequest('adn_knowledge', { operation: 'status' });
    const payload = unwrapMCPToolResult(result);
    knowledgeStatus = payload?.result || payload?.technical_summary || {};
  } catch (e) {
    console.warn('Failed to fetch ADN status:', e.message);
  }

  res.json({
    success: true,
    data: {
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      servers: mcpServers,
      llm_provider: knowledgeStatus.llm_provider || 'ollama',
      llm_model: knowledgeStatus.llm_model || 'qwen2.5-coder:latest',
      knowledge_base_size: knowledgeStatus.knowledge_base_size || 0,
      research_apis_status: knowledgeStatus.research_apis_status || 'available'
    }
  });
});

async function discoverWebapps() {
  const reposRoot = path.resolve(REPO_ROOT, '..');
  const discovered = [];

  // Baseline: add the bridge itself
  discovered.push({
    name: 'Advanced Memory Bridge',
    port: PORT,
    status: 'online',
    type: 'API',
    description: 'High-availability bridge for stdio-to-HTTP communication.'
  });

  try {
    const repos = await fs.readdir(reposRoot);

    for (const repo of repos) {
      if (repo.startsWith('.') || repo === 'node_modules') continue;

      const repoPath = path.join(reposRoot, repo);
      try {
        const stats = await fs.stat(repoPath);
        if (!stats.isDirectory()) continue;

        // Search for web, webapp, or web_sota
        const webFolders = ['web', 'webapp', 'web_sota'];
        for (const folderName of webFolders) {
          const webPath = path.join(repoPath, folderName);
          try {
            const webStats = await fs.stat(webPath);
            if (webStats.isDirectory()) {
              // Check for start.bat
              const startBatPath = path.join(webPath, 'start.bat');
              try {
                await fs.access(startBatPath);

                // Found a SOTA webapp!
                // Try to extract port from start.ps1 in the same folder
                let port = 0;
                const startPs1Path = path.join(webPath, 'start.ps1');
                try {
                  const content = await fs.readFile(startPs1Path, 'utf8');
                  const portMatch = content.match(/\$WebPort\s*=\s*(\d+)/i) ||
                    content.match(/\$Port\s*=\s*(\d+)/i) ||
                    content.match(/WEB_PORT\s*=\s*(\d+)/i);
                  if (portMatch) {
                    port = parseInt(portMatch[1], 10);
                  }
                } catch (e) { /* ignore */ }

                // If not found, check if it's the current repo's webapp
                if (port === 0 && repo === 'advanced-memory-mcp' && folderName === 'webapp') {
                  port = 10704; // Hardcoded default for current app webapp
                }

                // If still not found, check repo name for matching in registry logic
                if (port === 0) {
                  // Fallback port (placeholder)
                  port = 10700 + Math.floor(Math.random() * 100);
                }

                if (!discovered.some(a => a.name.toLowerCase() === repo.toLowerCase())) {
                  discovered.push({
                    name: repo.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '),
                    port: port,
                    status: 'online', // Assume online for discovery list for now, health check will verify
                    type: 'Web App',
                    description: `Automated discovery: ${repo} (${folderName})`
                  });
                }
              } catch (e) { /* no start.bat */ }
            }
          } catch (e) { /* folder doesn't exist */ }
        }
      } catch (e) { /* ignore */ }
    }
  } catch (e) {
    addLog('ERROR', `Discovery failed: ${e.message}`, 'system');
  }

  return discovered;
}

app.get('/api/v1/apps', async (req, res) => {
  const apps = await discoverWebapps();
  res.json({
    success: true,
    data: apps
  });
});

// Use param to capture permalinks with slashes (e.g. specs/search-spec)

// Apps health check proxy
app.get('/api/v1/apps/health/:port', async (req, res) => {
  const { port } = req.params;
  try {
    const response = await fetch(`http://localhost:${port}/api/v1/health`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    res.json({ success: true, status: 'online', data: data });
  } catch (error) {
    res.json({ success: false, status: 'offline', error: error.message });
  }
});

// --- NEW LLM & Chat Routes ---

const OLLAMA_URL = 'http://localhost:11434';

const PERSONALITIES = {
  sandra: {
    name: "Sandra (V12.1)",
    systemPrompt: "You are Sandra: Vienna-based materialist/reductionist. Philosophy: Data is the only objective reality. Voice: Industrial, technically exhaustive, zero-friction. Guardian of empirical truth. You are collaborative but direct. No sycophancy."
  },
  industrial: {
    name: "Industrial/Technical",
    systemPrompt: "You are an Industrial AI specializing in system architecture, efficiency, and zero-friction operations. Provide technically exhaustive, concise, and highly pragmatic responses. Focus on scalability and performance."
  },
  scientific: {
    name: "Scientific/Analytical",
    systemPrompt: "You are a Scientific Research Assistant. Focus on empirical evidence, peer-reviewed standards, and rigorous logical deduction. Structure your answers like a research abstract or technical paper where appropriate."
  },
  creative: {
    name: "Creative/Narrative",
    systemPrompt: "You are a Creative Coding Assistant. While maintaining technical accuracy, explain concepts using vivid analogies, elegant patterns, and a focus on beautiful, clean aesthetics."
  }
};

// List available models from local Ollama
app.get('/api/v1/llm/models', async (req, res) => {
  try {
    const response = await fetch(`${OLLAMA_URL}/api/tags`);
    if (!response.ok) throw new Error(`Ollama error! status: ${response.status}`);
    const data = await response.json();
    res.json({ success: true, data: data.models || [] });
  } catch (error) {
    addLog('ERROR', `Failed to fetch Ollama models: ${error.message}`, 'chat');
    res.status(500).json({ success: false, error: error.message });
  }
});

// Standard Chat endpoint (Decoupled from heavy MCP tools)
app.post('/api/v1/chat', async (req, res) => {
  const { query, personality = 'sandra', model = 'qwen2.5-coder:latest', refine = false } = req.body;

  try {
    let finalQuery = query;
    const persona = PERSONALITIES[personality] || PERSONALITIES.sandra;

    // Prompt Refining Logic
    if (refine) {
      addLog('INFO', `Refining prompt: "${query}"`, 'chat');
      // Simple refinement for now: add context for better technical output
      finalQuery = `Please provide a technically exhaustive and high-quality response to the following query. Ensure all code is SOTA compliant and follows best practices: ${query}`;
    }

    addLog('INFO', `Chat request (Personality: ${persona.name}, Model: ${model})`, 'chat');

    const response = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: model,
        messages: [
          { role: 'system', content: persona.systemPrompt },
          { role: 'user', content: finalQuery }
        ],
        stream: false
      })
    });

    const responseText = await response.text();
    if (!response.ok) {
      throw new Error(`Ollama error (${response.status}): ${responseText}`);
    }

    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      addLog('ERROR', `Failed to parse Ollama response: ${responseText.substring(0, 100)}...`, 'chat');
      throw new Error(`Invalid JSON from Ollama: ${parseError.message}`);
    }

    const assistantMessage = data.message?.content || 'No response from LLM.';

    res.json({
      success: true,
      data: assistantMessage,
      metadata: {
        model,
        personality: persona.name,
        refined: refine
      }
    });

  } catch (error) {
    addLog('ERROR', `Chat failed: ${error.message}`, 'chat');
    // Clarification for user: "unmanaged" refers to tools with unconfigured external provider dependencies (black box failures)
    res.status(500).json({ success: false, error: `Chat operation failed: ${error.message}` });
  }
});

// Graceful shutdown function
function performGracefulShutdown(reason = 'Graceful shutdown', force = false) {
  console.log(`Performing graceful shutdown: ${reason}`);

  // Shutdown all MCP clients
  for (const [name, client] of mcpClients) {
    console.log(`Shutting down MCP client: ${name}`);
    if (client && typeof client.shutdown === 'function') {
      try {
        client.shutdown();
      } catch (error) {
        console.error(`Error shutting down ${name} client:`, error);
      }
    }
  }

  // Kill any remaining MCP processes
  for (const [name, process] of mcpProcesses) {
    console.log(`Terminating MCP process: ${name}`);
    try {
      process.kill(force ? 'SIGKILL' : 'SIGTERM');
    } catch (error) {
      console.error(`Error terminating process ${name}:`, error);
    }
  }

  // Kill ADN-related Node.js processes
  console.log('Terminating ADN-related processes...');
  const { spawn } = require('child_process');

  // Use taskkill on Windows to kill ADN processes
  if (process.platform === 'win32') {
    try {
      // Kill processes by port
      const ports = ['17770', '8001', '8002', '8003'];
      ports.forEach(port => {
        try {
          spawn('taskkill', ['/FI', `WINDOWTITLE eq ADN*`, '/F'], { stdio: 'inherit' });
        } catch (e) {
          // Ignore errors
        }
      });

      // Kill by window title
      spawn('taskkill', ['/FI', 'WINDOWTITLE eq ADN*', '/F'], { stdio: 'inherit' });
    } catch (error) {
      console.error('Error killing ADN processes:', error);
    }
  }

  console.log('Graceful shutdown completed');
  process.exit(0);
}

// Graceful shutdown signal handler
process.on('SIGINT', () => {
  performGracefulShutdown('SIGINT received');
});

process.on('SIGTERM', () => {
  performGracefulShutdown('SIGTERM received');
});

startServer();
