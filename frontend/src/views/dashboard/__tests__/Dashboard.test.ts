import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Dashboard from '../Dashboard.vue'

vi.mock('@/components/dashboard/OverviewCards.vue', () => ({
  default: {
    name: 'OverviewCards',
    template: '<div class="overview-cards-mock">Overview Cards</div>'
  }
}))

vi.mock('@/components/dashboard/QuickActions.vue', () => ({
  default: {
    name: 'QuickActions',
    template: '<div class="quick-actions-mock">Quick Actions</div>'
  }
}))

vi.mock('@/components/charts/UsageTrendChart.vue', () => ({
  default: {
    name: 'UsageTrendChart',
    template: '<div class="usage-trend-chart-mock">Usage Trend Chart</div>'
  }
}))

vi.mock('@/components/charts/RevenueForecastChart.vue', () => ({
  default: {
    name: 'RevenueForecastChart',
    template: '<div class="revenue-forecast-chart-mock">Revenue Forecast Chart</div>'
  }
}))

vi.mock('@/components/charts/CustomerDistributionChart.vue', () => ({
  default: {
    name: 'CustomerDistributionChart',
    template: '<div class="customer-distribution-chart-mock">Customer Distribution Chart</div>'
  }
}))

vi.mock('@/components/charts/SettlementStatusChart.vue', () => ({
  default: {
    name: 'SettlementStatusChart',
    template: '<div class="settlement-status-chart-mock">Settlement Status Chart</div>'
  }
}))

describe('Dashboard.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders all sections correctly', () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: ['ARow', 'ACol', 'ACard']
      }
    })

    // 概览卡片
    expect(wrapper.find('.overview-cards-mock').exists()).toBe(true)
    
    // 四个图表
    expect(wrapper.find('.usage-trend-chart-mock').exists()).toBe(true)
    expect(wrapper.find('.revenue-forecast-chart-mock').exists()).toBe(true)
    expect(wrapper.find('.customer-distribution-chart-mock').exists()).toBe(true)
    expect(wrapper.find('.settlement-status-chart-mock').exists()).toBe(true)
    
    // 快捷操作
    expect(wrapper.find('.quick-actions-mock').exists()).toBe(true)
  })

  it('has correct layout structure', () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: ['ARow', 'ACol', 'ACard']
      }
    })

    const rows = wrapper.findAll('.ant-row')
    expect(rows.length).toBe(3) // 概览1行 + 图表2行
  })

  it('has correct padding and spacing', () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: ['ARow', 'ACol', 'ACard']
      }
    })

    const dashboardEl = wrapper.find('.dashboard')
    expect(dashboardEl.attributes('style')).toContain('padding: 24px')
  })
})