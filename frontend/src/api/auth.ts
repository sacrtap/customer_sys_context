import { request } from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    username: string
    email: string
    full_name?: string
  }
}

export interface UserInfo {
  id: string
  username: string
  email: string
  full_name?: string
  phone?: string
  is_active: boolean
  is_superuser: boolean
  roles: Array<{ id: string; name: string }>
  permissions: string[]
}

export const authApi = {
  login(data: LoginParams) {
    return request.post<LoginResponse>('/auth/login', data)
  },

  logout() {
    return request.post('/auth/logout')
  },

  getCurrentUser() {
    return request.get<UserInfo>('/auth/me')
  },
}
