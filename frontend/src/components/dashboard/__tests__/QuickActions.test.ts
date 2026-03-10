import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import QuickActions from '../QuickActions.vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'

vi.mock('ant-design-vue', async () => {
  const actual = await vi.importActual('ant-design-vue')
  return {
    ...actual,
    message: {
      success: vi.fn(),
      info: vi.fn(),
      error: vi.fn()
    }
  }
})

vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  }))
}))

describe('QuickActions.vue', () => {
  const routerPush = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    ;(useRouter as vi.Mock).mockReturnValue({ push: routerPush })
  })

  it('renders all four action buttons correctly', () => {
    const wrapper = mount(QuickActions)

    const buttons = wrapper.findAll('.action-card')
    expect(buttons.length).toBe(4)

    expect(buttons[0].text()).toContain('生成月度账单')
    expect(buttons[1].text()).toContain('导出结算报表')
    expect(buttons[2].text()).toContain('查看预警客户')
    expect(buttons[3].text()).toContain('导入客户数据')
  })

  it('opens generate bill modal when generate button is clicked', async () => {
    const wrapper = mount(QuickActions)

    await wrapper.find('.generate-bill-btn').trigger('click')
    
    expect(wrapper.find('.ant-modal-title').text()).toContain('生成月度账单')
    expect(wrapper.find('.ant-modal').exists()).toBe(true)
  })

  it('closes modal when cancel button is clicked', async () => {
    const wrapper = mount(QuickActions)

    await wrapper.find('.generate-bill-btn').trigger('click')
    expect(wrapper.find('.ant-modal').exists()).toBe(true)

    await wrapper.find('.ant-modal-footer .ant-btn-default').trigger('click')
    expect(wrapper.find('.ant-modal').exists()).toBe(false)
  })

  it('triggers bill generation and shows success message when confirm is clicked', async () => {
    const wrapper = mount(QuickActions)

    await wrapper.find('.generate-bill-btn').trigger('click')
    await wrapper.find('.ant-modal-footer .ant-btn-primary').trigger('click')

    await flushPromises()
    expect(message.success).toHaveBeenCalledWith('月度账单生成任务已启动')
    expect(wrapper.find('.ant-modal').exists()).toBe(false)
  })

  it('navigates to settlements export page when export button is clicked', async () => {
    const wrapper = mount(QuickActions)

    await wrapper.find('.export-report-btn').trigger('click')
    
    expect(routerPush).toHaveBeenCalledWith('/settlements?action=export')
  })

  it('navigates to customers warning page when warning button is clicked', async () => {
    const wrapper = mount(QuickActions)

    await wrapper.find('.warning-customers-btn').trigger('click')
    
    expect(routerPush).toHaveBeenCalledWith('/customers?health=warning')
  })

  it('opens import customer dialog when import button is clicked', async () => {
    const wrapper = mount(QuickActions, {
      global: {
        stubs: ['ImportCustomerDialog']
      }
    })

    await wrapper.find('.import-customers-btn').trigger('click')
    
    const dialog = wrapper.findComponent({ name: 'ImportCustomerDialog' })
    expect(dialog.exists()).toBe(true)
    expect(dialog.vm.visible).toBe(true)
  })

  it('shows success message when import completes', async () => {
    const wrapper = mount(QuickActions, {
      global: {
        stubs: ['ImportCustomerDialog']
      }
    })

    await wrapper.find('.import-customers-btn').trigger('click')
    const dialog = wrapper.findComponent({ name: 'ImportCustomerDialog' })
    await dialog.vm.$emit('success')

    expect(message.success).toHaveBeenCalledWith('客户数据导入成功')
  })
})