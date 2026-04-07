import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 1573,
    strictPort: true,
    proxy: {
      '/auth': {target: 'http://localhost:8000', changeOrigin: true},
      '/profile': {target: 'http://localhost:8000', changeOrigin: true},
    },
  },
})
