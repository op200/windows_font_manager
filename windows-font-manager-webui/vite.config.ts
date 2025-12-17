import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { resolve } from 'node:path'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },

  build: {
    target: 'es2020',
    outDir: resolve(__dirname, '../windows_font_manager/static'),
    emptyOutDir: true,
  },
  esbuild: {
    target: 'es2020',
  },

  server: {
    proxy: {
      '/ws': {
        target: 'http://localhost:8423',
        changeOrigin: true,
        ws: true,
        secure: false,
        // 添加重连和错误处理
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.error('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.error('Sending Request to the Target:', req.method, req.url);
          });
        }
      },
    },
  },
})
