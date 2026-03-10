import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import SettlementFilter from '../../../views/settlements/components/SettlementFilter.vue'

describe('SettlementFilter.vue', () => {
  it('renders all filter fields correctly', () => {
    const wrapper = mount(SettlementFilter)
    
    expect(wrapper.find('[placeholder="请选择客户"]').exists()).toBe(true)
    expect(wrapper.find('[placeholder="请选择状态"]').exists()).toBe(true)
    expect(wrapper.find('[placeholder="请选择月份"]').exists()).toBe(true)
    expect(wrapper.find('button[type="primary"]').text()).toContain('搜索')
    expect(wrapper.find('button').text()).toContain('重置')
  })

  it('emits search event with correct params when search button is clicked', async () => {
    const wrapper = mount(SettlementFilter)
    
    // 模拟输入筛选条件
    const customerSelect = wrapper.findComponent({ name: 'ASelect' })
    await customerSelect.vm.$emit('change', 'c1')
    
    const statusSelect = wrapper.findAllComponents({ name: 'ASelect' })[1]
    await statusSelect.vm.$emit('change', 'unsettled')
    
    const monthPicker = wrapper.findComponent({ name: 'AMonthPicker' })
    await monthPicker.vm.$emit('change', '2026-03')
    
    // 点击搜索
    await wrapper.find('button[type="primary"]').trigger('click')
    
    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('search')?.[0]).toEqual([{
      customer_id: 'c1',
      status: 'unsettled',
      month: '2026-03'
    }])
  })

  it('emits reset event when reset button is clicked', async () => {
    const wrapper = mount(SettlementFilter)
    
    // 先输入一些值
    const customerSelect = wrapper.findComponent({ name: 'ASelect' })
    await customerSelect.vm.$emit('change', 'c1')
    
    // 点击重置
    await wrapper.find('button:not([type="primary"])').trigger('click')
    
    expect(wrapper.emitted('reset')).toBeTruthy()
    
    // 确认搜索事件会被触发，参数为空
    expect(wrapper.emitted('search')).toBeTruthy()
    expect(wrapper.emitted('search')?.[0]).toEqual([{}])
  })
})
