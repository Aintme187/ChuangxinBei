import request from '@/utils/request.js'
import { useTokenStore } from '@/stores/token';
export const categoryService = () => {
    const tokenStore = useTokenStore();
    return request.get('/article/category', {
        header: {
            'Authorization' : tokenStore.token
        }
    });
}