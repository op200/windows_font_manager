import { resolve } from 'node:path'
import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

const proxy_target = 'http://localhost:8423'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },

  build: {
    target: 'es2020',
    outDir: resolve(import.meta.dirname, '../windows_font_manager/static'),
    emptyOutDir: true,
  },

  server: {
    proxy: {
      '/ws': {
        target: proxy_target,
        changeOrigin: true,
        ws: true,
        secure: false,
        // 添加重连和错误处理
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.error('proxy error', err)
          })
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.error('Sending Request to the Target:', req.method, req.url)
          })
        },
      },
      '/gv': {
        target: proxy_target,
        changeOrigin: true,
      },
      '/font': {
        target: proxy_target,
        changeOrigin: true,
      },
      '/font_info': {
        target: proxy_target,
        changeOrigin: true,
      },
    },
  },
})
