import { request } from '@/api/request'

export interface Customer {
  id: string
  name: string
  code: string
  contact_name?: string
  contact_phone?: string
  industry_id?: string
  level_id?: string
  status: 'active' | 'inactive'
  created_at: string
  updated_at: string
}

export interface CustomerListParams {
  page?: number
  page_size?: number
  search?: string
  status?: string
  industry_id?: string
  level_id?: string
}

export interface CustomerListResponse {
  items: Customer[]
  total: number
  page: number
  page_size: number
}

export const customerApi = {
  getList: (params?: CustomerListParams) => {
    return request.get<CustomerListResponse>('/customers', { params })
  },

  getDetail: (id: string) => {
    return request.get<Customer>(`/customers/${id}`)
  }
}
