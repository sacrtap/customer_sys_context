import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import RevenueForecastChart from '../RevenueForecastChart.vue'

// Mock ECharts component
vi.mock('vue-echarts', () => ({
  default: {
    name: 'v-chart',
    props: ['option', 'autoresize']
  }
}))

const mockData = [
  { month: '2026-01', actual: 12000, forecast: 0, lowerBound: 0, upperBound: 0 },
  { month: '2026-02', actual: 15000, forecast: 0, lowerBound: 0, upperBound: 0 },
  { month: '2026-03', actual: 18000, forecast: 0, lowerBound: 0, upperBound: 0 },
  { month: '2026-04', actual: 0, forecast: 20000, lowerBound: 18000, upperBound: 22000 },
  { month: '2026-05', actual: 0, forecast: 23000, lowerBound: 21000, upperBound: 25000 },
  { month: '2026-06', actual: 0, forecast: 25000, lowerBound: 22000, upperBound: 28000 }
]

describe('RevenueForecastChart', () => {
  it('renders correctly with empty data', () => {
    const wrapper = shallowMount(RevenueForecastChart, {
      props: {
        data: []
      }
    })
    expect(wrapper.find('.revenue-forecast-chart').exists()).toBe(true)
    expect(wrapper.find('.empty-state').exists()).toBe(true)
  })

  it('renders correctly with valid data', () => {
    const wrapper = shallowMount(RevenueForecastChart, {
      props: {
        data: mockData
      }
    })
    expect(wrapper.find('.revenue-forecast-chart').exists()).toBe(true)
    expect(wrapper.find('.chart-container').exists()).toBe(true)
  })

  it('shows loading state when loading prop is true', () => {
    const wrapper = shallowMount(RevenueForecastChart, {
      props: {
        data: [],
        loading: true
      }
    })
    expect(wrapper.find('.loading-container').exists()).toBe(true)
  })

  it('responds to data prop changes', async () => {
    const wrapper = shallowMount(RevenueForecastChart, {
      props: {
        data: []
      }
    })
    await wrapper.setProps({ data: mockData })
    expect(wrapper.vm.chartOption.xAxis.data).toHaveLength(6)
    expect(wrapper.vm.chartOption.series).toHaveLength(3) // actual, forecast, confidence band
  })

  it('supports different forecast periods', async () => {
    const wrapper = shallowMount(RevenueForecastChart, {
      props: {
        data: mockData,
        forecastPeriod: '3m'
      }
    })
    await wrapper.setProps({ forecastPeriod: '6m' })
    expect(wrapper.vm.forecastPeriod).toBe('6m')
  })

  it('emits periodChange event when forecast period is changed', async () => {
    const wrapper = shallowMount(RevenueForecastChart, {
      props: {
        data: mockData
      }
    })
    await wrapper.vm.handlePeriodChange('6m')
    expect(wrapper.emitted('periodChange')).toBeTruthy()
    expect(wrapper.emitted('periodChange')?.[0]).toEqual(['6m'])
  })
})
