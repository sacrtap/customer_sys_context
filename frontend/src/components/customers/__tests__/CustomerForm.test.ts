import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import Antd from 'ant-design-vue'
import CustomerForm from '../CustomerForm.vue'

describe('CustomerForm', () => {
  const mockCustomer = {
    id: '1',
    customer_code: 'C001',
    customer_name: '测试客户',
    industry: { id: '1', name: '房地产' },
    level: { id: '1', code: 'A', name: 'A级' },
    contact_person: '张三',
    contact_phone: '13800138000',
    email: 'test@example.com',
    address: '北京市朝阳区',
    remark: '测试备注'
  }

  const mountOptions = {
    global: {
      plugins: [Antd]
    }
  }

  it('renders all form fields in create mode', () => {
    const wrapper = mount(CustomerForm, { ...mountOptions, props: { mode: 'create' } })
    
    expect(wrapper.find('[data-testid="customer-code"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="customer-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="industry"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="customer-level"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="contact-person"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="contact-phone"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="email"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="address"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="remark"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="submit-btn"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="cancel-btn"]').exists()).toBe(true)
  })

  it('prefills form data in edit mode', () => {
    const wrapper = mount(CustomerForm, { 
      ...mountOptions,
      props: { 
        mode: 'edit',
        customer: mockCustomer
      } 
    })

    expect(wrapper.find<HTMLInputElement>('[data-testid="customer-code"] input').element.value).toBe('C001')
    expect(wrapper.find<HTMLInputElement>('[data-testid="customer-name"] input').element.value).toBe('测试客户')
    expect(wrapper.find<HTMLInputElement>('[data-testid="contact-person"] input').element.value).toBe('张三')
    expect(wrapper.find<HTMLInputElement>('[data-testid="contact-phone"] input').element.value).toBe('13800138000')
    expect(wrapper.find<HTMLInputElement>('[data-testid="email"] input').element.value).toBe('test@example.com')
    expect(wrapper.find<HTMLInputElement>('[data-testid="address"] textarea').element.value).toBe('北京市朝阳区')
    expect(wrapper.find<HTMLInputElement>('[data-testid="remark"] textarea').element.value).toBe('测试备注')
  })

  it('validates required fields on submit', async () => {
    const wrapper = mount(CustomerForm, { ...mountOptions, props: { mode: 'create' } })
    const submitBtn = wrapper.find('[data-testid="submit-btn"]')

    await submitBtn.trigger('click')
    await vi.waitFor(() => {
      expect(wrapper.find('.ant-form-item-explain').exists()).toBe(true)
    })
  })

  it('validates phone number format', async () => {
    const wrapper = mount(CustomerForm, { ...mountOptions, props: { mode: 'create' } })
    const phoneInput = wrapper.find('[data-testid="contact-phone"] input')
    
    await phoneInput.setValue('123456')
    await phoneInput.trigger('blur')
    
    await vi.waitFor(() => {
      expect(wrapper.find('.ant-form-item-explain-error').text()).toContain('手机号格式不正确')
    })
  })

  it('validates email format', async () => {
    const wrapper = mount(CustomerForm, { ...mountOptions, props: { mode: 'create' } })
    const emailInput = wrapper.find('[data-testid="email"] input')
    
    await emailInput.setValue('invalid-email')
    await emailInput.trigger('blur')
    
    await vi.waitFor(() => {
      expect(wrapper.find('.ant-form-item-explain-error').text()).toContain('邮箱格式不正确')
    })
  })

  it('emits submit event with form data when validation passes', async () => {
    const wrapper = mount(CustomerForm, { ...mountOptions, props: { mode: 'create' } })
    
    await wrapper.find('[data-testid="customer-code"] input').setValue('C002')
    await wrapper.find('[data-testid="customer-name"] input').setValue('新客户')
    await wrapper.find('[data-testid="contact-person"] input').setValue('李四')
    await wrapper.find('[data-testid="contact-phone"] input').setValue('13900139000')
    await wrapper.find('[data-testid="email"] input').setValue('new@example.com')
    await wrapper.find('[data-testid="address"] textarea').setValue('上海市浦东新区')
    
    await wrapper.find('[data-testid="submit-btn"]').trigger('click')
    
    await vi.waitFor(() => {
      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')?.[0][0]).toEqual(expect.objectContaining({
        customer_code: 'C002',
        customer_name: '新客户',
        contact_person: '李四',
        contact_phone: '13900139000',
        email: 'new@example.com',
        address: '上海市浦东新区'
      }))
    }, { timeout: 2000 })
  })

  it('emits cancel event when cancel button is clicked', async () => {
    const wrapper = mount(CustomerForm, { ...mountOptions, props: { mode: 'create' } })
    
    await wrapper.find('[data-testid="cancel-btn"]').trigger('click')
    
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })
})
