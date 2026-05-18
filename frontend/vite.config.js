import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 1573,
    strictPort: true,
    proxy: {
      '/auth':            { target: 'http://localhost:8000', changeOrigin: true },
      '/profile':         { target: 'http://localhost:8000', changeOrigin: true },
      '/restaurants':     { target: 'http://localhost:8000', changeOrigin: true },
      '/cart':            { target: 'http://localhost:8000', changeOrigin: true },
      '/checkout':        { target: 'http://localhost:8000', changeOrigin: true },
      '/orders':          { target: 'http://localhost:8000', changeOrigin: true },
      '/payment':         { target: 'http://localhost:8000', changeOrigin: true },
      '/recently-viewed': { target: 'http://localhost:8000', changeOrigin: true },
      '/favourites':      { target: 'http://localhost:8000', changeOrigin: true },
      '/notifications':   { target: 'http://localhost:8000', changeOrigin: true },
      '/deliveries':      { target: 'http://localhost:8000', changeOrigin: true },
      '/reviews':         { target: 'http://localhost:8000', changeOrigin: true },
      '/coupons':         { target: 'http://localhost:8000', changeOrigin: true },
      '/admin':           { target: 'http://localhost:8000', changeOrigin: true },
      '/users':           { target: 'http://localhost:8000', changeOrigin: true },
      '/health':          { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
