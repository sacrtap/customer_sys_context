import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi, type UserInfo } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isLoggedIn = ref(!!token.value)

  async function login(username: string, password: string) {
    const response = await authApi.login({ username, password })
    
    if (response.access_token) {
      localStorage.setItem('access_token', response.access_token)
      token.value = response.access_token
      isLoggedIn.value = true
      user.value = response.user as unknown as UserInfo
    }
    
    return response
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (e) {
      // 忽略错误
    } finally {
      localStorage.removeItem('access_token')
      token.value = null
      isLoggedIn.value = false
      user.value = null
    }
  }

  async function fetchCurrentUser() {
    try {
      const response = await authApi.getCurrentUser()
      user.value = response
      return response
    } catch (e) {
      logout()
      throw e
    }
  }

  function hasPermission(permission: string): boolean {
    if (!user.value) return false
    if (user.value.is_superuser) return true
    return user.value.permissions.includes(permission)
  }

  return {
    user,
    token,
    isLoggedIn,
    login,
    logout,
    fetchCurrentUser,
    hasPermission,
  }
})
