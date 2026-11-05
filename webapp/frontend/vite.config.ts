import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/embed': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/extension': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
});
