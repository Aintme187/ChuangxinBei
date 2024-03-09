//导入vue-router
import { createRouter, createWebHistory } from 'vue-router'
//导入组件
import LoginVue from '@/views/Login.vue'
import LayoutVue from '@/views/Layout.vue'
import ArticleCategory from '@/views/ArticleCategory.vue';
import ArticleManage from '@/views/ArticleManage.vue';
import ChangeAvatar from '@/views/ChangeAvatar.vue';
import ChangePassword from '@/views/ChangePassword.vue';
import UserInfo from '@/views/UserInfo.vue';
const routes = [
    {path:'/login', component: LoginVue},
    {
        path:'/',
        component: LayoutVue,
        children:[
            {path:'/article/category', component: ArticleCategory},
            {path:'/article/manage', component: ArticleManage},
            {path:'/user/info', component: UserInfo},
            {path:'/user/changeavatar', component: ChangeAvatar},
            {path:'/user/changepassword', component: ChangePassword}
        ]
        
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes: routes
});

export default router