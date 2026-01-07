import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)
    const token = ref(localStorage.getItem('token') || '')

    const setUser = (userData) => {
        user.value = userData
    }

    const setToken = (tokenValue) => {
        token.value = tokenValue
        localStorage.setItem('token', tokenValue)
    }

    const clearUser = () => {
        user.value = null
        token.value = ''
        localStorage.removeItem('token')
    }

    return {
        user,
        token,
        setUser,
        setToken,
        clearUser
    }
})
