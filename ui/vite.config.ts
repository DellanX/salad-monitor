import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.url, './src')
    }
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true
  },
  css: {
    postcss: './postcss.config.js'
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8765',
        changeOrigin: true,
        secure: false,
      }
    },
    hmr: true,
    watch: {
      usePolling: true,
    }
  }
})
