import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 10704,
    host: '0.0.0.0', // Bind to all interfaces for Tailnet access
    strictPort: true,
    proxy: {
      // FastAPI (advanced_memory.server:app) default port 10705 — see webapp/start.ps1
      '/api': {
        target: 'http://127.0.0.1:10705',
        changeOrigin: true,
      },
    },
    allowedHosts: [
      '*', // Allow all hosts for Tailnet
      'goliath' // Allow goliath hostname for Tailnet access
    ],
    cors: {
      origin: true, // Allow all origins for Tailnet
      credentials: true
    },
    hmr: {
      // No host override: 0.0.0.0 is a bind-only address, never a valid thing
      // for a browser to connect its HMR websocket to - hardcoding it here
      // broke HMR for every client (local and Tailnet alike), which is why
      // the console showed a permanent "WebSocket connection to
      // ws://0.0.0.0:24678 failed" on every page load. Omitting `host`
      // makes Vite's client fall back to `location.hostname`, which is
      // exactly right for both local (127.0.0.1/localhost) and Tailnet
      // (whatever hostname the browser actually used to load the page).
      port: 24678
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['lucide-react'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom', 'axios', 'lucide-react'],
  },
})
