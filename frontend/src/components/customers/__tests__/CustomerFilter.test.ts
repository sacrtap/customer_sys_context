import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import Antd from 'ant-design-vue'
import CustomerFilter from '../CustomerFilter.vue'

describe('CustomerFilter', () => {
  const mountOptions = {
    global: {
      plugins: [Antd]
    }
  }

  it('renders all filter fields', () => {
    const wrapper = mount(CustomerFilter, mountOptions)
    
    expect(wrapper.find('[data-testid="industry-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="level-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="settlement-status-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="status-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="owner-filter"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="search-btn"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="reset-btn"]').exists()).toBe(true)
  })

  it('emits search event with filter values when search button is clicked', async () => {
    const wrapper = mount(CustomerFilter, mountOptions)
    
    await wrapper.find('[data-testid="industry-filter"]').setValue('1')
    await wrapper.find('[data-testid="level-filter"]').setValue('2')
    await wrapper.find('[data-testid="status-filter"]').setValue('active')
    
    await wrapper.find('[data-testid="search-btn"]').trigger('click')
    
    await vi.waitFor(() => {
      expect(wrapper.emitted('search')).toBeTruthy()
      expect(wrapper.emitted('search')?.[0][0]).toEqual(expect.objectContaining({
        industry_id: '1',
        level_id: '2',
        status: 'active'
      }))
    })
  })

  it('resets all filters and emits reset event when reset button is clicked', async () => {
    const wrapper = mount(CustomerFilter, mountOptions)
    
    await wrapper.find('[data-testid="industry-filter"]').setValue('1')
    await wrapper.find('[data-testid="level-filter"]').setValue('2')
    await wrapper.find('[data-testid="status-filter"]').setValue('active')
    
    await wrapper.find('[data-testid="reset-btn"]').trigger('click')
    
    expect(wrapper.find<HTMLSelectElement>('[data-testid="industry-filter"]').element.value).toBe('')
    expect(wrapper.find<HTMLSelectElement>('[data-testid="level-filter"]').element.value).toBe('')
    expect(wrapper.find<HTMLSelectElement>('[data-testid="status-filter"]').element.value).toBe('')
    expect(wrapper.emitted('reset')).toBeTruthy()
  })

  it('emits update:filters event when filter values change', async () => {
    const wrapper = mount(CustomerFilter, mountOptions)
    
    await wrapper.find('[data-testid="industry-filter"]').setValue('1')
    
    await vi.waitFor(() => {
      expect(wrapper.emitted('update:filters')).toBeTruthy()
      expect(wrapper.emitted('update:filters')?.[0][0]).toEqual(expect.objectContaining({
        industry_id: '1'
      }))
    })
  })
})
