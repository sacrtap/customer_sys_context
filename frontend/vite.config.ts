/// <reference types="vitest" />
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  // 生产环境移除 console 和 debugger
  esbuild: {
    drop: ['console', 'debugger'],
  },
  build: {
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 启用压缩
    minify: 'esbuild',
    // 启用报告生成，方便分析包体积
    reportCompressedSize: true,
    // 小于 4kb 的资源内联为 base64
    assetsInlineLimit: 4096,
    rollupOptions: {
      output: {
        // 代码分割，分离第三方依赖
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ant-design-vue': ['ant-design-vue'],
          'echarts': ['echarts', 'vue-echarts'],
          'utils': ['axios', 'dayjs'],
        },
        // 静态资源分类存放
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'happy-dom',
    globals: true,
  },
})
