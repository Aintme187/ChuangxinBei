//导入vue-router
import { createRouter, createWebHistory } from 'vue-router'
//导入组件
import LoginVue from '@/views/Login.vue'
import LayoutVue from '@/views/Layout.vue'
import Noise from '@/views/Noise.vue';
import Backdoor from "@/views/Backdoor.vue";
const routes = [
    {path:'/login', component: LoginVue},
    {
        path: '/',
        component: LayoutVue,
        redirect: '/attack/noise',
        children: [
            {path: '/attack/noise', component: Noise},
        ]
    },
    {
        path:'/',
        component: LayoutVue,
        redirect: '/attack/backdoor',
        children:[
            {path:'/attack/backdoor', component: Backdoor},
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes: routes
});

export default router