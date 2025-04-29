import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tsConfigPaths from 'vite-tsconfig-paths'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tsConfigPaths()],
  server: {
    port: 3002,
    proxy: {
      '/api': { //  Все запросы, начинающиеся с /api, будут проксироваться
        target: 'http://localhost:3001', //  Адрес твоего Flask API
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '') //  Удаляем /api из URL
      }
    }
  }
})