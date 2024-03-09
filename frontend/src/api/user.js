import request from '@/utils/request.js'
export const registerService = (registerData) => {
    let params = new URLSearchParams();
    for(let key in registerData) {
        params.append(key, registerData[key]);
    }
    return request.post('user/register', params);
}

export const loginService = (registerData) => {
    let params = new URLSearchParams();
    for(let key in registerData){
        params.append(key, registerData[key]);
    }
    return request.post('user/login', params);
}