import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import SettlementStatusChart from '../SettlementStatusChart.vue'

// Mock ECharts component
vi.mock('vue-echarts', () => ({
  default: {
    name: 'v-chart',
    props: ['option', 'autoresize']
  }
}))

const mockData = [
  { month: '2026-01', settled: 150000, unsettled: 50000 },
  { month: '2026-02', settled: 180000, unsettled: 30000 },
  { month: '2026-03', settled: 220000, unsettled: 80000 },
  { month: '2026-04', settled: 200000, unsettled: 60000 },
  { month: '2026-05', settled: 250000, unsettled: 40000 },
  { month: '2026-06', settled: 280000, unsettled: 70000 }
]

describe('SettlementStatusChart', () => {
  it('renders correctly with empty data', () => {
    const wrapper = shallowMount(SettlementStatusChart, {
      props: {
        data: []
      }
    })
    expect(wrapper.find('.settlement-status-chart').exists()).toBe(true)
    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })

  it('renders correctly with valid data', () => {
    const wrapper = shallowMount(SettlementStatusChart, {
      props: {
        data: mockData
      }
    })
    expect(wrapper.find('.settlement-status-chart').exists()).toBe(true)
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('shows loading state when loading prop is true', () => {
    const wrapper = shallowMount(SettlementStatusChart, {
      props: {
        data: [],
        loading: true
      }
    })
    expect(wrapper.find('.loading-container').exists()).toBe(true)
  })

  it('responds to data prop changes', async () => {
    const wrapper = shallowMount(SettlementStatusChart, {
      props: {
        data: []
      }
    })
    await wrapper.setProps({ data: mockData })
    expect(wrapper.vm.chartOption.xAxis.data).toHaveLength(6)
    expect(wrapper.vm.chartOption.series).toHaveLength(2)
  })

  it('supports annual summary view', async () => {
    const wrapper = shallowMount(SettlementStatusChart, {
      props: {
        data: mockData,
        viewType: 'monthly'
      }
    })
    await wrapper.setProps({ viewType: 'annual' })
    expect(wrapper.vm.viewType).toBe('annual')
  })

  it('emits viewTypeChange event when view type is changed', async () => {
    const wrapper = shallowMount(SettlementStatusChart, {
      props: {
        data: mockData
      }
    })
    await wrapper.vm.handleViewTypeChange('annual')
    expect(wrapper.emitted('viewTypeChange')).toBeTruthy()
    expect(wrapper.emitted('viewTypeChange')?.[0]).toEqual(['annual'])
  })

  it('calculates total correctly', () => {
    const wrapper = shallowMount(SettlementStatusChart, {
      props: {
        data: mockData
      }
    })
    expect(wrapper.vm.totalSettled).toBe(1280000)
    expect(wrapper.vm.totalUnsettled).toBe(330000)
  })
})
