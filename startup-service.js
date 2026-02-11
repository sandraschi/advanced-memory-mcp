const express = require('express')
const { spawn } = require('child_process')
const cors = require('cors')
const path = require('path')

const app = express()
app.use(cors())
app.use(express.json())

let bridgeProcess = null

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'running', service: 'startup-service' })
})

// Start bridge server endpoint
app.post('/start-bridge', (req, res) => {
  try {
    if (bridgeProcess) {
      console.log('Bridge server already running')
      return res.json({ success: true, message: 'Bridge server already running' })
    }

    console.log('Starting ADN MCP Bridge Server...')

    // Start the bridge server
    bridgeProcess = spawn('node', ['bridge-server.js'], {
      cwd: __dirname,
      detached: false,
      stdio: ['pipe', 'pipe', 'pipe']
    })

    bridgeProcess.on('error', (err) => {
      console.error('Failed to start bridge server:', err)
    })

    bridgeProcess.on('exit', (code) => {
      console.log(`Bridge server exited with code ${code}`)
      bridgeProcess = null
    })

    bridgeProcess.stdout.on('data', (data) => {
      console.log(`Bridge: ${data}`)
    })

    bridgeProcess.stderr.on('data', (data) => {
      console.error(`Bridge Error: ${data}`)
    })

    // Wait a moment for startup
    setTimeout(() => {
      res.json({
        success: true,
        message: 'Bridge server start initiated',
        pid: bridgeProcess ? bridgeProcess.pid : null
      })
    }, 1000)

  } catch (error) {
    console.error('Error starting bridge server:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Stop bridge server endpoint
app.post('/stop-bridge', (req, res) => {
  try {
    if (bridgeProcess) {
      bridgeProcess.kill()
      bridgeProcess = null
      res.json({ success: true, message: 'Bridge server stopped' })
    } else {
      res.json({ success: true, message: 'Bridge server not running' })
    }
  } catch (error) {
    console.error('Error stopping bridge server:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Start the startup service - bind to all interfaces for Tailnet access
const PORT = parseInt(process.env.ADN_STARTUP_PORT, 10) || 10733
app.listen(PORT, '0.0.0.0', () => {
  console.log(`ADN Startup Service running on http://0.0.0.0:${PORT} (Tailnet accessible)`)
  console.log(`POST /start-bridge to start the bridge server`)
  console.log(`POST /stop-bridge to stop the bridge server`)
})
