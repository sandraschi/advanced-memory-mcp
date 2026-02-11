const express = require('express')
const { spawn } = require('child_process')
const cors = require('cors')
const path = require('path')

const app = express()
app.use(cors())
app.use(express.json())

let startupServiceProcess = null
let bridgeServerProcess = null

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'running',
    service: 'auto-start-service',
    startupService: startupServiceProcess ? 'running' : 'stopped',
    bridgeServer: bridgeServerProcess ? 'running' : 'stopped'
  })
})

// Auto-start all services endpoint
app.post('/start-all', (req, res) => {
  try {
    console.log('Starting all ADN services...')

    // Start startup service if not running
    if (!startupServiceProcess) {
      console.log('Starting startup service...')
      startupServiceProcess = spawn('node', ['startup-service.js'], {
        cwd: __dirname,
        detached: false,
        stdio: ['pipe', 'pipe', 'pipe']
      })

      startupServiceProcess.on('error', (err) => {
        console.error('Startup service error:', err)
      })

      startupServiceProcess.on('exit', (code) => {
        console.log(`Startup service exited with code ${code}`)
        startupServiceProcess = null
      })

      startupServiceProcess.stdout.on('data', (data) => {
        console.log(`Startup Service: ${data}`)
      })

      startupServiceProcess.stderr.on('data', (data) => {
        console.error(`Startup Service Error: ${data}`)
      })
    }

    // Give startup service time to listen, then start bridge via 10733/start-bridge, then webapp
    setTimeout(async () => {
      try {
        console.log('Starting bridge via startup service...')
        const bridgeRes = await fetch('http://localhost:10733/start-bridge', { method: 'POST' })
        if (bridgeRes.ok) {
          console.log('Bridge start initiated')
        } else {
          console.warn('Bridge start returned', bridgeRes.status)
        }
      } catch (e) {
        console.warn('Could not start bridge via 10733:', e.message)
      }

      console.log('Starting webapp...')
      const webappProcess = spawn('npm', ['run', 'dev'], {
        cwd: path.join(__dirname, 'webapp'),
        detached: true,
        stdio: 'ignore'
      })

      webappProcess.on('error', (err) => {
        console.error('Webapp start error:', err)
      })

      res.json({
        success: true,
        message: 'All services started',
        services: {
          startupService: startupServiceProcess ? startupServiceProcess.pid : null,
          webapp: webappProcess ? webappProcess.pid : null
        }
      })
    }, 2000)

  } catch (error) {
    console.error('Error starting services:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Stop all services endpoint
app.post('/stop-all', (req, res) => {
  try {
    console.log('Stopping all services...')

    if (startupServiceProcess) {
      startupServiceProcess.kill()
      startupServiceProcess = null
    }

    if (bridgeServerProcess) {
      bridgeServerProcess.kill()
      bridgeServerProcess = null
    }

    res.json({ success: true, message: 'All services stopped' })
  } catch (error) {
    console.error('Error stopping services:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Start the auto-start service - bind to all interfaces for Tailnet access
const PORT = parseInt(process.env.ADN_AUTOSTART_PORT, 10) || 10735
app.listen(PORT, '0.0.0.0', () => {
  console.log(`ADN Auto-Start Service running on http://0.0.0.0:${PORT} (Tailnet accessible)`)
  console.log(`POST /start-all to start all services`)
  console.log(`POST /stop-all to stop all services`)
})
