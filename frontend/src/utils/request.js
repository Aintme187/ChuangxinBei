//定制请求的实例

//导入axios 
import axios from 'axios';
import { useTokenStore } from '@/stores/token';
//定义一个变量,记录公共的前缀  ,  baseURL
const baseURL = '/api';
const instance = axios.create({baseURL})

//添加请求拦截器
instance.interceptors.request.use(
    (config) => {
        let tokenStore = useTokenStore;
        if(tokenStore.token){
            config.headers.Authorization = tokenStore.token;
        }
        return config;
    },
    (err) => {
        Promise.reject(err);
    }
)
//添加响应拦截器
instance.interceptors.response.use(
    result => {
    //如果业务状态码为0，代表本次操作成功
    if (result.data.code == 0) {
        return result.data;
    }

    //代码走到这里，代表业务状态码不是0，本次操作失败
    alert(result.data.message || '服务异常');
        return Promise.reject(result.data);//异步的状态转化成失败的状态
    },

    err => {
        alert('服务异常');
        return Promise.reject(err);//异步的状态转化成失败的状态
    }
   )

export default instance;