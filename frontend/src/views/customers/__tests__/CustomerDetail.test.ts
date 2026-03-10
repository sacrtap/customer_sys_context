import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import Antd from 'ant-design-vue'
import { createRouter, createWebHistory } from 'vue-router'
import CustomerDetail from '../CustomerDetail.vue'
import UsageTrendChart from '@/components/charts/UsageTrendChart.vue'

// Mock Vue Router
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/customers/:id', component: CustomerDetail },
    { path: '/settlements/:id', component: { template: '<div></div>' } }
  ]
})

vi.mock('@/api/request', () => ({
  request: {
    get: vi.fn((url) => {
      if (url.includes('/customers/1')) {
        return Promise.resolve({
          id: '1',
          customer_code: 'C001',
          customer_name: '测试客户',
          industry: { name: '房地产' },
          level: { name: 'A级' },
          status: 'active',
          settlement_status: 'settled',
          contact_person: '张三',
          contact_phone: '13800138000',
          contact_email: 'test@example.com',
          address: '北京市朝阳区',
          owner: { full_name: '管理员' },
          created_at: '2024-01-01',
          remark: '测试备注'
        })
      } else if (url.includes('/usage-trend')) {
        return Promise.resolve({
          items: [
            { date: '2024-01', usageCount: 100, amount: 1000 },
            { date: '2024-02', usageCount: 200, amount: 2000 }
          ]
        })
      } else if (url.includes('/settlements')) {
        return Promise.resolve({
          items: [
            { id: '1', month: '2024-01', amount: 1000, status: 'settled', created_at: '2024-02-01', paid_at: '2024-02-05' },
            { id: '2', month: '2024-02', amount: 2000, status: 'unsettled', created_at: '2024-03-01' }
          ],
          total: 2
        })
      }
      return Promise.reject(new Error('Not found'))
    })
  }
}))

describe('CustomerDetail', () => {
  const mountOptions = {
    global: {
      plugins: [Antd, router],
      stubs: {
        UsageTrendChart: true
      }
    }
  }

  it('renders customer basic information correctly', async () => {
    router.push('/customers/1')
    await router.isReady()
    
    const wrapper = mount(CustomerDetail, mountOptions)
    
    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('测试客户')
      expect(wrapper.text()).toContain('C001')
      expect(wrapper.text()).toContain('房地产')
      expect(wrapper.text()).toContain('A级')
      expect(wrapper.text()).toContain('张三')
      expect(wrapper.text()).toContain('13800138000')
      expect(wrapper.text()).toContain('test@example.com')
    })
  })

  it('renders usage trend chart component', async () => {
    router.push('/customers/1')
    await router.isReady()
    
    const wrapper = mount(CustomerDetail, mountOptions)
    
    await vi.waitFor(() => {
      expect(wrapper.findComponent(UsageTrendChart).exists()).toBe(true)
    })
  })

  it('renders settlement records table with data', async () => {
    router.push('/customers/1')
    await router.isReady()
    
    const wrapper = mount(CustomerDetail, mountOptions)
    
    await vi.waitFor(() => {
      const table = wrapper.find('.ant-table')
      expect(table.exists()).toBe(true)
      expect(table.text()).toContain('2024-01')
      expect(table.text()).toContain('¥1000.00')
      expect(table.text()).toContain('已结算')
      expect(table.text()).toContain('2024-02')
      expect(table.text()).toContain('¥2000.00')
      expect(table.text()).toContain('未结算')
    })
  })

  it('has edit and export usage buttons', async () => {
    router.push('/customers/1')
    await router.isReady()
    
    const wrapper = mount(CustomerDetail, mountOptions)
    
    await vi.waitFor(() => {
      const buttons = wrapper.findAll('.ant-btn')
      expect(buttons.some(btn => btn.text() === '编辑')).toBe(true)
      expect(buttons.some(btn => btn.text() === '导出用量')).toBe(true)
      expect(buttons.some(btn => btn.text() === '返回列表')).toBe(true)
    })
  })

  it('triggers export functionality when export button is clicked', async () => {
    router.push('/customers/1')
    await router.isReady()
    
    // Mock window.URL.createObjectURL
    global.URL.createObjectURL = vi.fn(() => 'blob:test')
    global.URL.revokeObjectURL = vi.fn()
    
    const wrapper = mount(CustomerDetail, mountOptions)
    
    await vi.waitFor(async () => {
      const exportBtn = wrapper.find('.ant-btn').filter(btn => btn.text() === '导出用量')
      await exportBtn.trigger('click')
      expect(global.URL.createObjectURL).toHaveBeenCalled()
    })
  })
})
