import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTokenStore = defineStore('token', () => {
    const token = ref('');

    const setToken = (newToken) => {
        token.value = newToken;
    }

    const removeToken = () => {
        token.value = '';
    }

    /*defineStore返回值描述：
        返回的是一个函数，将来可以调用该函数，得到第二个参数中返回的内容
        如果不return的话是不是就无法用·去解析调用token,setToken,removeToken三个属性了
    */
    return{
        token, setToken, removeToken
    }
})