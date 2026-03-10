import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { message } from 'ant-design-vue'
import PaymentConfirmDialog from '../../../views/settlements/components/PaymentConfirmDialog.vue'
import { settlementApi } from '@/api/settlement'

vi.mock('@/api/settlement', () => ({
  settlementApi: {
    confirmPayment: vi.fn()
  }
}))

vi.mock('ant-design-vue', async () => {
  const actual = await vi.importActual('ant-design-vue')
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn()
    }
  }
})

const mockSettlement = {
  id: '1',
  customer_id: 'c1',
  customer_name: '测试客户1',
  month: '2026-03',
  amount: 10000,
  status: 'unsettled',
  created_at: '2026-03-01T00:00:00Z',
  updated_at: '2026-03-01T00:00:00Z'
}

describe('PaymentConfirmDialog.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(settlementApi.confirmPayment as vi.Mock).mockResolvedValue({})
  })

  it('renders correctly when open', () => {
    const wrapper = mount(PaymentConfirmDialog, {
      props: {
        open: true,
        settlement: mockSettlement
      }
    })

    expect(wrapper.find('.ant-modal-title').text()).toContain('确认支付')
    expect(wrapper.text()).toContain('测试客户1')
    expect(wrapper.text()).toContain('2026-03')
    expect(wrapper.text()).toContain('¥10,000')
    expect(wrapper.find('[placeholder="请输入实付金额"]').exists()).toBe(true)
    expect(wrapper.find('[placeholder="请选择支付日期"]').exists()).toBe(true)
    expect(wrapper.find('[placeholder="请输入备注"]').exists()).toBe(true)
  })

  it('validates required fields before submission', async () => {
    const wrapper = mount(PaymentConfirmDialog, {
      props: {
        open: true,
        settlement: mockSettlement
      }
    })

    // 直接点击确定
    await wrapper.find('.ant-btn-primary').trigger('click')
    await flushPromises()

    expect(settlementApi.confirmPayment).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('请输入实付金额')
    expect(wrapper.text()).toContain('请选择支付日期')
  })

  it('validates amount is positive number', async () => {
    const wrapper = mount(PaymentConfirmDialog, {
      props: {
        open: true,
        settlement: mockSettlement
      }
    })

    // 输入负数金额
    const amountInput = wrapper.find('input[placeholder="请输入实付金额"]')
    await amountInput.setValue('-100')
    
    const datePicker = wrapper.findComponent({ name: 'ADatePicker' })
    await datePicker.vm.$emit('change', '2026-03-15')
    
    await wrapper.find('.ant-btn-primary').trigger('click')
    await flushPromises()

    expect(settlementApi.confirmPayment).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('实付金额必须大于0')
  })

  it('submits successfully with valid data', async () => {
    const wrapper = mount(PaymentConfirmDialog, {
      props: {
        open: true,
        settlement: mockSettlement
      }
    })

    // 输入正确数据
    const amountInput = wrapper.find('input[placeholder="请输入实付金额"]')
    await amountInput.setValue('10000')
    
    const datePicker = wrapper.findComponent({ name: 'ADatePicker' })
    await datePicker.vm.$emit('change', '2026-03-15')
    
    const remarkInput = wrapper.find('textarea[placeholder="请输入备注"]')
    await remarkInput.setValue('已收到转账')
    
    await wrapper.find('.ant-btn-primary').trigger('click')
    await flushPromises()

    expect(settlementApi.confirmPayment).toHaveBeenCalledWith('1', {
      paid_amount: 10000,
      paid_at: '2026-03-15',
      remark: '已收到转账'
    })
    expect(wrapper.emitted('success')).toBeTruthy()
    expect(wrapper.emitted('update:open')).toBeTruthy()
    expect(wrapper.emitted('update:open')?.[0]).toEqual([false])
  })

  it('closes dialog when cancel button is clicked', async () => {
    const wrapper = mount(PaymentConfirmDialog, {
      props: {
        open: true,
        settlement: mockSettlement
      }
    })

    await wrapper.find('.ant-btn-default').trigger('click')
    
    expect(wrapper.emitted('update:open')).toBeTruthy()
    expect(wrapper.emitted('update:open')?.[0]).toEqual([false])
  })
})
