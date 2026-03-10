import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import UsageTrendChart from '../UsageTrendChart.vue'

// Mock ECharts component
vi.mock('vue-echarts', () => ({
  default: {
    name: 'v-chart',
    props: ['option', 'autoresize']
  }
}))

const mockData = [
  { date: '2026-03-01', usageCount: 120, amount: 5000 },
  { date: '2026-03-02', usageCount: 150, amount: 6200 },
  { date: '2026-03-03', usageCount: 180, amount: 7500 },
  { date: '2026-03-04', usageCount: 160, amount: 6800 },
  { date: '2026-03-05', usageCount: 200, amount: 8500 }
]

describe('UsageTrendChart', () => {
  it('renders correctly with empty data', () => {
    const wrapper = shallowMount(UsageTrendChart, {
      props: {
        data: []
      }
    })
    expect(wrapper.find('.usage-trend-chart').exists()).toBe(true)
    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })

  it('renders correctly with valid data', () => {
    const wrapper = shallowMount(UsageTrendChart, {
      props: {
        data: mockData
      }
    })
    expect(wrapper.find('.usage-trend-chart').exists()).toBe(true)
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('shows loading state when loading prop is true', () => {
    const wrapper = shallowMount(UsageTrendChart, {
      props: {
        data: [],
        loading: true
      }
    })
    expect(wrapper.find('.loading-container').exists()).toBe(true)
  })

  it('responds to data prop changes', async () => {
    const wrapper = shallowMount(UsageTrendChart, {
      props: {
        data: []
      }
    })
    await wrapper.setProps({ data: mockData })
    expect(wrapper.vm.chartOption.xAxis.data).toHaveLength(5)
    expect(wrapper.vm.chartOption.series).toHaveLength(2)
  })

  it('emits dateRangeChange event when time range is changed', async () => {
    const wrapper = shallowMount(UsageTrendChart, {
      props: {
        data: mockData,
        dateRange: ['2026-03-01', '2026-03-05']
      }
    })
    await wrapper.vm.handleDateRangeChange(['2026-02-01', '2026-02-28'])
    expect(wrapper.emitted('dateRangeChange')).toBeTruthy()
    expect(wrapper.emitted('dateRangeChange')?.[0]).toEqual([['2026-02-01', '2026-02-28']])
  })

  it('supports multi-customer comparison mode', () => {
    const multiCustomerData = [
      { date: '2026-03-01', customerA: 120, customerB: 90 },
      { date: '2026-03-02', customerA: 150, customerB: 110 }
    ]
    const wrapper = shallowMount(UsageTrendChart, {
      props: {
        data: multiCustomerData,
        compareMode: true
      }
    })
    expect(wrapper.vm.chartOption.series).toHaveLength(2)
    expect(wrapper.vm.chartOption.legend.data).toEqual(['customerA', 'customerB'])
  })
})
