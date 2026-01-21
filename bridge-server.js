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
const PORT = 8001; // Different from main server port 8000

app.use(cors());
app.use(express.json());

// Store active MCP processes
const mcpProcesses = new Map();

// Get skill directory path for a given folder
function getSkillDirectory(folderName) {
  // Skills are in the folders you specified
  const userHome = process.env.USERPROFILE || process.env.HOME;
  console.log(`Getting skill directory for ${folderName}, userHome: ${userHome}`);

  switch (folderName) {
    case 'cursor-skills':
      return path.join(userHome, '.cursor', 'skills-cursor');
    case 'windsurf-skills':
      return path.join(userHome, '.codeium', 'windsurf', 'skills');
    case 'adn-skills':
      return path.join(__dirname, 'skills');
    case 'antigravity-skills':
      return path.join(userHome, '.gemini', 'antigravity', 'skills');
    default:
      return null;
  }
}

// Scan skill directory for SKILL.md files
async function scanSkillDirectory(skillDir, folderName) {
  const skills = [];

  try {
    console.log(`Attempting to access skill directory: ${skillDir}`);
    // Check if directory exists
    await fs.access(skillDir);
    console.log(`Directory ${skillDir} exists, reading contents...`);

    // Read directory contents
    const entries = await fs.readdir(skillDir, { withFileTypes: true });
    console.log(`Found ${entries.length} entries in ${skillDir}`);

    for (const entry of entries) {
      if (entry.isDirectory()) {
        const skillPath = path.join(skillDir, entry.name);
        const skillMdPath = path.join(skillPath, 'SKILL.md');
        console.log(`Checking skill: ${entry.name} at ${skillMdPath}`);

        try {
          // Check if SKILL.md exists
          await fs.access(skillMdPath);
          console.log(`Found SKILL.md for ${entry.name}`);

          // Read SKILL.md content
          const content = await fs.readFile(skillMdPath, 'utf8');
          console.log(`Read ${content.length} characters from ${skillMdPath}`);

          // Parse frontmatter (simple parsing)
          const skillData = parseSkillFrontmatter(content, folderName);
          if (skillData) {
            skillData.filePath = path.relative(__dirname, skillMdPath);
            skills.push(skillData);
            console.log(`Successfully parsed skill: ${skillData.title}`);
          } else {
            console.log(`Failed to parse skill data for ${entry.name}`);
          }
        } catch (error) {
          console.log(`SKILL.md not found or unreadable for ${entry.name}:`, error.message);
          continue;
        }
      } else {
        console.log(`Skipping non-directory entry: ${entry.name}`);
      }
    }
  } catch (error) {
    // Directory doesn't exist or can't be read
    console.log(`Skill directory ${skillDir} not accessible:`, error.message);
  }

  console.log(`Returning ${skills.length} skills from ${skillDir}`);
  return skills;
}

// Parse SKILL.md frontmatter and content
function parseSkillFrontmatter(content, folderName) {
  try {
    console.log('Parsing skill content, length:', content.length);

    // Simple frontmatter parsing (between --- markers)
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);

    if (!frontmatterMatch) {
      console.log('No frontmatter found, returning null');
      return null;
    }

    const frontmatter = frontmatterMatch[1];
    const body = frontmatterMatch[2];
    console.log('Frontmatter:', frontmatter.substring(0, 100));
    console.log('Body length:', body.length);

    // Parse YAML-like frontmatter
    const metadata = {};
    const lines = frontmatter.split('\n');

    for (const line of lines) {
      const colonIndex = line.indexOf(':');
      if (colonIndex > 0) {
        const key = line.substring(0, colonIndex).trim();
        const value = line.substring(colonIndex + 1).trim().replace(/^["']|["']$/g, '');
        metadata[key] = value;
        console.log(`Parsed metadata: ${key} = ${value}`);
      }
    }

    const skillData = {
      id: Date.now() + Math.random(), // Simple ID generation
      title: metadata.name || metadata.title || 'Untitled Skill',
      description: metadata.description || '',
      folder: folderName,
      tags: metadata.tags ? metadata.tags.split(',').map(t => t.trim()) : [],
      created: metadata.created || new Date().toISOString(),
      modified: metadata.modified || new Date().toISOString(),
      content: body.trim()
    };

    console.log('Returning skill data:', skillData.title);
    return skillData;
  } catch (error) {
    console.error('Error parsing skill frontmatter:', error);
    return null;
  }
}

// Initialize MCP server process
function startMCPProcess() {
  return new Promise((resolve, reject) => {
    console.log('Starting ADN MCP server...');

    // Use the direct Python script instead of inline code
    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(__dirname, 'src', 'advanced_memory', 'mcp', 'server.py');

    console.log(`Running: ${pythonPath} ${scriptPath}`);

    const mcpProcess = spawn(pythonPath, [scriptPath], {
      cwd: __dirname,
      stdio: ['pipe', 'pipe', 'pipe'],
      env: {
        ...process.env,
        PYTHONPATH: path.join(__dirname, 'src')
      }
    });

    // Handle MCP server output
    mcpProcess.stdout.on('data', (data) => {
      const chunk = data.toString();
      console.log('MCP stdout:', chunk.substring(0, 100) + (chunk.length > 100 ? '...' : ''));
    });

    mcpProcess.stderr.on('data', (data) => {
      const error = data.toString();
      console.error('MCP stderr:', error);

      // Some stderr output is normal during startup
      if (error.includes('error') || error.includes('Error') || error.includes('Exception')) {
        console.error('MCP process error detected:', error);
      }
    });

    mcpProcess.on('close', (code) => {
      console.log(`MCP process exited with code ${code}`);
      mcpProcesses.delete('main');
    });

    mcpProcess.on('error', (error) => {
      console.error('Failed to start MCP process:', error);
      reject(error);
    });

    mcpProcesses.set('main', mcpProcess);

    // Resolve immediately since we're using mock responses anyway
    console.log('MCP process started (using mock responses for now)');
    resolve(mcpProcess);
  });
}

// MCP communication helper - proper JSON-RPC implementation
async function sendMCPRequest(toolName, params = {}) {
  const mcpProcess = mcpProcesses.get('main');
  if (!mcpProcess) {
    throw new Error('MCP server not running');
  }

  return new Promise((resolve, reject) => {
    const requestId = Date.now().toString();
    console.log(`Calling MCP tool: ${toolName} with params:`, params);

    // FastMCP uses JSON-RPC 2.0 over stdio
    const jsonRpcRequest = {
      jsonrpc: '2.0',
      id: requestId,
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: params
      }
    };

    const requestJson = JSON.stringify(jsonRpcRequest);
    const requestMessage = `Content-Length: ${Buffer.byteLength(requestJson, 'utf8')}\r\n\r\n${requestJson}`;

    console.log('Sending MCP request:', requestMessage);

    let responseBuffer = '';
    let contentLength = 0;
    let headersParsed = false;

    const responseHandler = (data) => {
      const chunk = data.toString();
      console.log('MCP response chunk:', chunk.substring(0, 200) + (chunk.length > 200 ? '...' : ''));

      responseBuffer += chunk;

      // Parse MCP protocol (similar to HTTP)
      if (!headersParsed) {
        const headerEndIndex = responseBuffer.indexOf('\r\n\r\n');
        if (headerEndIndex !== -1) {
          const headers = responseBuffer.substring(0, headerEndIndex);
          const contentLengthMatch = headers.match(/Content-Length:\s*(\d+)/i);

          if (contentLengthMatch) {
            contentLength = parseInt(contentLengthMatch[1]);
            headersParsed = true;

            const bodyStart = headerEndIndex + 4;
            const body = responseBuffer.substring(bodyStart);

            if (body.length >= contentLength) {
              // We have the complete response
              try {
                const response = JSON.parse(body.substring(0, contentLength));
                mcpProcess.stdout.removeListener('data', responseHandler);

                if (response.id === requestId) {
                  if (response.error) {
                    reject(new Error(`MCP Error: ${response.error.message}`));
                  } else {
                    resolve(response.result);
                  }
                }
              } catch (parseError) {
                console.error('Failed to parse MCP response:', parseError);
                reject(parseError);
              }
            }
          }
        }
      } else if (responseBuffer.length >= contentLength) {
        // Headers already parsed, check if we have complete body
        try {
          const response = JSON.parse(responseBuffer);
          mcpProcess.stdout.removeListener('data', responseHandler);

          if (response.id === requestId) {
            if (response.error) {
              reject(new Error(`MCP Error: ${response.error.message}`));
            } else {
              resolve(response.result);
            }
          }
        } catch (parseError) {
          console.error('Failed to parse MCP response:', parseError);
          reject(parseError);
        }
      }
    };

    mcpProcess.stdout.on('data', responseHandler);

    // Send the request
    mcpProcess.stdin.write(requestMessage);

    // Timeout after 30 seconds
    setTimeout(() => {
      mcpProcess.stdout.removeListener('data', responseHandler);
      reject(new Error('MCP request timeout'));
    }, 30000);
  });
}

// Removed mock responses - now using real MCP communication

// API Routes
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    bridge: 'running',
    mcp: mcpProcesses.has('main') ? 'connected' : 'disconnected'
  });
});

// Notes routes - now using real MCP communication
app.get('/api/v1/notes', async (req, res) => {
  try {
    // Ensure MCP is initialized
    await ensureMCPInitialized();

    console.log('Fetching notes via MCP...');
    const mcpResponse = await sendMCPRequest('adn_search', {
      operation: 'notes',
      query: req.query.query || '',
      page: parseInt(req.query.page) || 1,
      page_size: parseInt(req.query.limit) || 10
    });

    console.log('MCP search response:', mcpResponse);

    // Format MCP response for webapp
    const notes = [];
    if (mcpResponse && Array.isArray(mcpResponse)) {
      mcpResponse.forEach(item => {
        if (item && typeof item === 'object') {
          notes.push({
            id: item.id || item.permalink || item.title?.toLowerCase().replace(/\s+/g, '-'),
            title: item.title || 'Untitled',
            content: item.content || item.summary || '',
            tags: Array.isArray(item.tags) ? item.tags : [],
            created: item.created || item.date || new Date().toISOString(),
            modified: item.modified || item.updated || new Date().toISOString(),
            permalink: item.permalink || item.id
          });
        }
      });
    }

    res.json({
      success: true,
      data: {
        notes: notes,
        total: notes.length,
        page: 1,
        pages: 1
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

app.get('/api/v1/notes/:id', async (req, res) => {
  try {
    // Ensure MCP is initialized
    await ensureMCPInitialized();

    console.log(`Fetching note ${req.params.id} via MCP...`);
    const mcpResponse = await sendMCPRequest('adn_content', {
      operation: 'read',
      identifier: req.params.id
    });

    console.log('MCP content response:', mcpResponse);

    if (mcpResponse && typeof mcpResponse === 'object') {
      const noteData = {
        id: mcpResponse.id || req.params.id,
        title: mcpResponse.title || 'Untitled',
        content: mcpResponse.content || mcpResponse.text || '',
        tags: Array.isArray(mcpResponse.tags) ? mcpResponse.tags : [],
        created: mcpResponse.created || mcpResponse.date || new Date().toISOString(),
        modified: mcpResponse.modified || mcpResponse.updated || new Date().toISOString(),
        permalink: mcpResponse.permalink || mcpResponse.id
      };

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

// Initialize MCP server on first request
let mcpInitialized = false;

async function ensureMCPInitialized() {
  if (!mcpInitialized && !mcpProcesses.has('main')) {
    try {
      console.log('Initializing MCP server...');
      await startMCPProcess();
      mcpInitialized = true;
      console.log('MCP server initialized successfully');
    } catch (error) {
      console.error('Failed to initialize MCP server:', error);
      throw error;
    }
  }
}

// Start server
async function startServer() {
  console.log('Starting ADN MCP Bridge Server...');

  // Start HTTP server - bind to all interfaces for Tailnet access
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`ADN MCP Bridge Server running on http://0.0.0.0:${PORT} (Tailnet accessible)`);
    console.log('MCP server will be initialized on first request');
  });
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('Shutting down bridge server...');

  // Kill MCP processes
  for (const [name, process] of mcpProcesses) {
    console.log(`Terminating MCP process: ${name}`);
    process.kill();
  }

  process.exit(0);
});

startServer();
