import request from '@/utils/request.js'
import {API_URL} from "@/views/global.vue";
//axios.defaults.withCredentials = true

export const get_csrf_token = () => {
    request.get(API_URL+"/get_csrf_token/") //待定
    let cookie = document.cookie
    //console.log('cookie_csrf_token=' + csrf_token)
    return cookie.split('=')[1]
}