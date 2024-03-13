import request from '@/utils/request.js'

//axios.defaults.withCredentials = true

export const get_csrf_token = () => {
    request.get("http://localhost:8000/get_csrf_token/") //待定
    let cookie = document.cookie
    //console.log('cookie_csrf_token=' + csrf_token)
    return cookie.split('=')[1]
}