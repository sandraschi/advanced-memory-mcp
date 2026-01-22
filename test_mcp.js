// Simple test to check MCP server
const { spawn } = require('child_process');
const path = require('path');

console.log('Testing MCP server...');

const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
const scriptPath = path.join(__dirname, 'src', 'advanced_memory', 'mcp', 'server.py');

console.log(`Starting: ${pythonPath} ${scriptPath}`);

const mcpProcess = spawn(pythonPath, [scriptPath], {
  cwd: __dirname,
  stdio: ['pipe', 'pipe', 'pipe'],
  env: {
    ...process.env,
    PYTHONPATH: path.join(__dirname, 'src')
  }
});

mcpProcess.stderr.on('data', (data) => {
  console.error('STDERR:', data.toString());
});

mcpProcess.stdout.on('data', (data) => {
  console.log('STDOUT received:', data.length, 'bytes');
  console.log('Data:', data.toString());
});

// Send initialize message after a delay
setTimeout(() => {
  console.log('Sending initialize message...');
  const initMessage = `Content-Length: 157\r\n\r\n{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"tools":{},"prompts":{}},"clientInfo":{"name":"Test","version":"1.0"}}}`;

  console.log('Message to send:', initMessage);
  mcpProcess.stdin.write(initMessage);

  // Exit after a few seconds
  setTimeout(() => {
    mcpProcess.kill();
    process.exit(0);
  }, 3000);
}, 2000);
