import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)
    const token = ref(localStorage.getItem('token') || '')

    // 计算属性：是否已登录
    const isLoggedIn = computed(() => !!token.value)

    const setUser = (userData) => {
        user.value = userData
    }

    const setToken = (tokenValue) => {
        token.value = tokenValue
        if (tokenValue) {
            localStorage.setItem('token', tokenValue)
        } else {
            localStorage.removeItem('token')
        }
    }

    const logout = () => {
        user.value = null
        token.value = ''
        localStorage.removeItem('token')
        localStorage.removeItem('refresh_token')
    }

    // 别名保持兼容
    const clearUser = logout

    return {
        user,
        token,
        isLoggedIn,
        setUser,
        setToken,
        logout,
        clearUser
    }
})
