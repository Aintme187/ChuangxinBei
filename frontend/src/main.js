import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from '@/router'
import { createPinia } from 'pinia'
// 起名叫index的好处就是这里import不需要加文件名，单文件创建的范式
const app = createApp(App)
const pinia = createPinia()
//第三方库下载需要在app这里调用才能使用，createApp的作用
app.use(router)
app.use(ElementPlus)
app.use(pinia)
app.mount('#app')
