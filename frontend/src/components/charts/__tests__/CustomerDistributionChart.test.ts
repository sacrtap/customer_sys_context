import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import CustomerDistributionChart from '../CustomerDistributionChart.vue'

// Mock ECharts component
vi.mock('vue-echarts', () => ({
  default: {
    name: 'v-chart',
    props: ['option', 'autoresize']
  }
}))

const mockIndustryData = [
  { name: '住宅地产', value: 45, percentage: 45 },
  { name: '商业地产', value: 30, percentage: 30 },
  { name: '工业地产', value: 15, percentage: 15 },
  { name: '文旅地产', value: 10, percentage: 10 }
]

const mockLevelData = [
  { name: 'VIP客户', value: 20, percentage: 20 },
  { name: '核心客户', value: 35, percentage: 35 },
  { name: '重要客户', value: 30, percentage: 30 },
  { name: '普通客户', value: 15, percentage: 15 }
]

describe('CustomerDistributionChart', () => {
  it('renders correctly with empty data', () => {
    const wrapper = shallowMount(CustomerDistributionChart, {
      props: {
        data: []
      }
    })
    expect(wrapper.find('.customer-distribution-chart').exists()).toBe(true)
    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })

  it('renders correctly with industry data', () => {
    const wrapper = shallowMount(CustomerDistributionChart, {
      props: {
        data: mockIndustryData,
        dimension: 'industry'
      }
    })
    expect(wrapper.find('.customer-distribution-chart').exists()).toBe(true)
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('renders correctly with level data', () => {
    const wrapper = shallowMount(CustomerDistributionChart, {
      props: {
        data: mockLevelData,
        dimension: 'level'
      }
    })
    expect(wrapper.find('.customer-distribution-chart').exists()).toBe(true)
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('shows loading state when loading prop is true', () => {
    const wrapper = shallowMount(CustomerDistributionChart, {
      props: {
        data: [],
        loading: true
      }
    })
    expect(wrapper.find('.loading-container').exists()).toBe(true)
  })

  it('supports switching between dimensions', async () => {
    const wrapper = shallowMount(CustomerDistributionChart, {
      props: {
        data: mockIndustryData,
        dimension: 'industry'
      }
    })
    await wrapper.setProps({ data: mockLevelData, dimension: 'level' })
    expect(wrapper.vm.chartOption.series[0].data).toHaveLength(4)
    expect(wrapper.vm.chartOption.title.text).toContain('客户等级分布')
  })

  it('emits dimensionChange event when dimension is switched', async () => {
    const wrapper = shallowMount(CustomerDistributionChart, {
      props: {
        data: mockIndustryData
      }
    })
    await wrapper.vm.handleDimensionChange('level')
    expect(wrapper.emitted('dimensionChange')).toBeTruthy()
    expect(wrapper.emitted('dimensionChange')?.[0]).toEqual(['level'])
  })

  it('supports pie and ring chart types', async () => {
    const wrapper = shallowMount(CustomerDistributionChart, {
      props: {
        data: mockIndustryData,
        chartType: 'pie'
      }
    })
    await wrapper.setProps({ chartType: 'ring' })
    expect(wrapper.vm.chartOption.series[0].radius).toEqual(['40%', '70%'])
  })
})
