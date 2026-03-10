import request from '@/api/request'

// 数据类型定义
export interface UsageTrendData {
  date: string
  usageCount: number
  amount: number
  [key: string]: any
}

export interface RevenueForecastData {
  month: string
  actual: number
  forecast: number
  lowerBound: number
  upperBound: number
}

export interface CustomerDistributionData {
  name: string
  value: number
  percentage: number
}

export interface SettlementStatusData {
  month: string
  settled: number
  unsettled: number
}

export interface OverviewTrend {
  totalCustomers: number
  monthlyRevenue: number
  pendingSettlement: number
  healthWarning: number
}

export interface OverviewData {
  totalCustomers: number
  monthlyRevenue: number
  pendingSettlement: number
  healthWarning: number
  trends: OverviewTrend
}

// API请求
export const dashboardApi = {
  getUsageTrend: (params?: {
    dateRange?: [string, string]
    customerIds?: number[]
  }) => {
    return request.get<UsageTrendData[]>('/dashboard/usage-trend', { params })
  },

  getRevenueForecast: (params?: {
    period?: '1m' | '3m' | '6m'
  }) => {
    return request.get<RevenueForecastData[]>('/dashboard/revenue-forecast', { params })
  },

  getCustomerDistribution: (params?: {
    dimension?: 'industry' | 'level'
  }) => {
    return request.get<CustomerDistributionData[]>('/dashboard/customer-distribution', { params })
  },

  getSettlementStatus: (params?: {
    viewType?: 'monthly' | 'annual'
    year?: number
  }) => {
    return request.get<SettlementStatusData[]>('/dashboard/settlement-status', { params })
  },

  getOverview: () => {
    return request.get<OverviewData>('/dashboard/overview')
  }
}
