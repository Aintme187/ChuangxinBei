//导入vue-router
import {createRouter, createWebHistory} from 'vue-router'
//导入组件
import LoginVue from '@/views/Login.vue'
import LayoutVue from '@/views/Layout.vue'
import Noise from '@/views/Noise.vue';
import Backdoor from "@/views/Backdoor.vue";
import {attacking, axios, API_URL} from "@/views/global.vue";
import {ref} from "vue";

const routes = [
    {path: '/login', component: LoginVue},
    {
        path: '/',
        component: LayoutVue,
        redirect: '/attack/noise',
        children: [
            {path: '/attack/noise', component: Noise},
        ]
    },
    {
        path: '/',
        component: LayoutVue,
        redirect: '/attack/backdoor',
        children: [
            {path: '/attack/backdoor', component: Backdoor},
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes: routes
});

// add Before Guards to stop attack silently
router.beforeEach(() => {
    // stop silently
    axios({
        method: 'get',
        url: API_URL + '/stop/',
    }).then((request) => {
        const dataGet = request.data
        if (dataGet['code'] === -1) {
            alert(dataGet['msg'])
        } else if (attacking && attacking.value) {
            attacking.value = false
        }
    })
})

export default router