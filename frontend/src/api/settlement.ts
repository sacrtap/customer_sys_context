import { request } from '@/api/request'

export interface Settlement {
  id: string
  customer_id: string
  customer_name: string
  month: string
  amount: number
  status: 'settled' | 'unsettled'
  settled_at?: string
  remark?: string
  created_at: string
  updated_at: string
}

export interface SettlementListParams {
  customer_id?: string
  status?: string
  month?: string
  page?: number
  page_size?: number
}

export interface SettlementListResponse {
  items: Settlement[]
  total: number
  page: number
  page_size: number
}

export interface SettlementCreate {
  customer_id: string
  month: string
  amount: number
  remark?: string
}

export interface SettlementUpdate extends Partial<SettlementCreate> {
  id: string
}

export interface PaymentConfirmRequest {
  paid_amount: number
  paid_at: string
  remark?: string
}

export interface MonthlyBillGenerateRequest {
  year: number
  month: number
  customer_ids?: string[]
}

export interface MonthlyBillGenerateResult {
  success_count: number
  skipped_count: number
  errors: Array<{ customer_id: string; error: string }>
}

export interface ExportSettlementRequest {
  customer_ids?: string[]
  start_date?: string
  end_date?: string
  status?: string
}

export const settlementApi = {
  getList: (params?: SettlementListParams) => {
    return request.get<SettlementListResponse>('/settlements', { params })
  },

  getDetail: (id: string) => {
    return request.get<Settlement>(`/settlements/${id}`)
  },

  create: (data: SettlementCreate) => {
    return request.post<Settlement>('/settlements', data)
  },

  update: (id: string, data: SettlementUpdate) => {
    return request.put<Settlement>(`/settlements/${id}`, data)
  },

  delete: (id: string) => {
    return request.delete(`/settlements/${id}`)
  },

  confirmPayment: (id: string, data: PaymentConfirmRequest) => {
    return request.post<Settlement>(`/settlements/${id}/confirm-payment`, data)
  },

  generateMonthlyBills: (data: MonthlyBillGenerateRequest) => {
    return request.post<MonthlyBillGenerateResult>('/settlements/generate-monthly', data)
  },

  export: (data: ExportSettlementRequest) => {
    return request.post<Blob>('/settlements/export', data, {
      responseType: 'blob'
    })
  }
}
