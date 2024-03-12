import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

// icon

import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'



// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    , AutoImport({
      resolvers: [ // 自动导入图标组件
    
        IconsResolver({
          prefix: 'Icon',
        }),
        ElementPlusResolver()
      ],
    }),
    Components({
      resolvers: [ // 自动注册图标组件
        IconsResolver({
          enabledCollections: ['ep'],
        })
        , ElementPlusResolver()
      ],

    }),
    Icons({
      autoInstall: true,
    }),
  ],
  server: {
    host: '0.0.0.0', // ip
    port: 5173,  
    hmr: true,  // 热启动
    open: true // 自动打开浏览器
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
