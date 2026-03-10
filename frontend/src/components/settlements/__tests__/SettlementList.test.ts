import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { message } from 'ant-design-vue'
import SettlementList from '../../views/settlements/SettlementList.vue'
import { settlementApi } from '@/api/settlement'

vi.mock('@/api/settlement', () => ({
  settlementApi: {
    getList: vi.fn()
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

const mockSettlements = [
  {
    id: '1',
    customer_id: 'c1',
    customer_name: '测试客户1',
    month: '2026-03',
    amount: 10000,
    status: 'unsettled',
    created_at: '2026-03-01T00:00:00Z',
    updated_at: '2026-03-01T00:00:00Z'
  },
  {
    id: '2',
    customer_id: 'c2',
    customer_name: '测试客户2',
    month: '2026-03',
    amount: 20000,
    status: 'settled',
    settled_at: '2026-03-10T00:00:00Z',
    created_at: '2026-03-01T00:00:00Z',
    updated_at: '2026-03-10T00:00:00Z'
  }
]

describe('SettlementList.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(settlementApi.getList as vi.Mock).mockResolvedValue({
      items: mockSettlements,
      total: 2,
      page: 1,
      page_size: 20
    })
  })

  it('renders empty state when no data', async () => {
    ;(settlementApi.getList as vi.Mock).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 20
    })

    const wrapper = mount(SettlementList, {
      global: {
        stubs: ['SettlementFilter', 'PaymentConfirmDialog']
      }
    })
    await flushPromises()

    expect(wrapper.find('.ant-empty').exists()).toBe(true)
  })

  it('renders settlement list correctly with data', async () => {
    const wrapper = mount(SettlementList, {
      global: {
        stubs: ['SettlementFilter', 'PaymentConfirmDialog']
      }
    })
    await flushPromises()

    const table = wrapper.find('.ant-table')
    expect(table.exists()).toBe(true)
    
    const rows = table.findAll('.ant-table-tbody tr')
    expect(rows.length).toBe(2)
    
    expect(rows[0].text()).toContain('测试客户1')
    expect(rows[0].text()).toContain('2026-03')
    expect(rows[0].text()).toContain('10000')
    expect(rows[0].text()).toContain('未结算')
    
    expect(rows[1].text()).toContain('测试客户2')
    expect(rows[1].text()).toContain('2026-03')
    expect(rows[1].text()).toContain('20000')
    expect(rows[1].text()).toContain('已结算')
  })

  it('shows loading state when fetching data', async () => {
    let resolvePromise: (value: any) => void
    const promise = new Promise(resolve => {
      resolvePromise = resolve
    })
    ;(settlementApi.getList as vi.Mock).mockReturnValue(promise)

    const wrapper = mount(SettlementList, {
      global: {
        stubs: ['SettlementFilter', 'PaymentConfirmDialog']
      }
    })

    expect(wrapper.find('.ant-spin-spinning').exists()).toBe(true)
    
    resolvePromise!({
      items: mockSettlements,
      total: 2,
      page: 1,
      page_size: 20
    })
    await flushPromises()
    
    expect(wrapper.find('.ant-spin-spinning').exists()).toBe(false)
  })

  it('shows correct action buttons based on status', async () => {
    const wrapper = mount(SettlementList, {
      global: {
        stubs: ['SettlementFilter', 'PaymentConfirmDialog']
      }
    })
    await flushPromises()

    const rows = wrapper.findAll('.ant-table-tbody tr')
    
    // 未结算的行有确认支付按钮
    expect(rows[0].text()).toContain('确认支付')
    // 已结算的行没有确认支付按钮
    expect(rows[1].text()).not.toContain('确认支付')
    
    // 都有详情和删除按钮
    expect(rows[0].text()).toContain('详情')
    expect(rows[0].text()).toContain('删除')
    expect(rows[1].text()).toContain('详情')
    expect(rows[1].text()).toContain('删除')
  })

  it('triggers search when filter emits search event', async () => {
    const wrapper = mount(SettlementList, {
      global: {
        stubs: ['PaymentConfirmDialog']
      }
    })
    await flushPromises()

    const filter = wrapper.findComponent({ name: 'SettlementFilter' })
    await filter.vm.$emit('search', { status: 'unsettled' })
    
    expect(settlementApi.getList).toHaveBeenCalledWith(expect.objectContaining({
      status: 'unsettled',
      page: 1
    }))
  })

  it('resets filter when filter emits reset event', async () => {
    const wrapper = mount(SettlementList, {
      global: {
        stubs: ['PaymentConfirmDialog']
      }
    })
    await flushPromises()

    const filter = wrapper.findComponent({ name: 'SettlementFilter' })
    await filter.vm.$emit('reset')
    
    expect(settlementApi.getList).toHaveBeenCalledWith(expect.objectContaining({
      page: 1
    }))
  })

  it('changes page when table pagination changes', async () => {
    const wrapper = mount(SettlementList, {
      global: {
        stubs: ['SettlementFilter', 'PaymentConfirmDialog']
      }
    })
    await flushPromises()

    const table = wrapper.findComponent({ name: 'ATable' })
    await table.vm.$emit('change', { current: 2, pageSize: 20 })
    
    expect(settlementApi.getList).toHaveBeenCalledWith(expect.objectContaining({
      page: 2,
      page_size: 20
    }))
  })
})
