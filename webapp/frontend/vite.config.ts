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
      host: '0.0.0.0', // HMR over Tailnet
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
