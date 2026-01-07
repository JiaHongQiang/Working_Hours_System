import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
    baseURL: '/api',
    timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 响应拦截器
request.interceptors.response.use(
    response => {
        return response
    },
    async error => {
        const originalRequest = error.config

        // 如果是401错误且不是刷新token的请求
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
                try {
                    // 尝试刷新token
                    const response = await axios.post('/api/token/refresh/', {
                        refresh: refreshToken
                    })

                    const { access } = response.data
                    localStorage.setItem('token', access)

                    // 使用新token重试原请求
                    originalRequest.headers.Authorization = `Bearer ${access}`
                    return request(originalRequest)
                } catch (refreshError) {
                    // 刷新失败，清除token并跳转登录
                    localStorage.removeItem('token')
                    localStorage.removeItem('refresh_token')
                    window.location.href = '/login'
                    return Promise.reject(refreshError)
                }
            } else {
                // 没有refresh token，直接跳转登录
                localStorage.removeItem('token')
                window.location.href = '/login'
            }
        }

        // 其他错误
        const message = error.response?.data?.detail || error.response?.data?.error || error.message || '请求失败'
        ElMessage.error(message)

        return Promise.reject(error)
    }
)

export default request
