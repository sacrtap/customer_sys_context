import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import OverviewCards from '../OverviewCards.vue'
import { dashboardApi } from '@/api/dashboard'
import { useRouter } from 'vue-router'

vi.mock('@/api/dashboard', () => ({
  dashboardApi: {
    getOverview: vi.fn()
  }
}))

vi.mock('vue-router', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  }))
}))

const mockOverviewData = {
  totalCustomers: 1320,
  monthlyRevenue: 256800,
  pendingSettlement: 89500,
  healthWarning: 12,
  trends: {
    totalCustomers: 5.2,
    monthlyRevenue: 12.8,
    pendingSettlement: -3.5,
    healthWarning: 8.3
  }
}

describe('OverviewCards.vue', () => {
  const routerPush = vi.fn()
  
  beforeEach(() => {
    vi.clearAllMocks()
    ;(useRouter as vi.Mock).mockReturnValue({ push: routerPush })
    ;(dashboardApi.getOverview as vi.Mock).mockResolvedValue(mockOverviewData)
  })

  it('renders loading state when fetching data', () => {
    let resolvePromise: (value: any) => void
    const promise = new Promise(resolve => {
      resolvePromise = resolve
    })
    ;(dashboardApi.getOverview as vi.Mock).mockReturnValue(promise)

    const wrapper = mount(OverviewCards)
    
    expect(wrapper.find('.ant-skeleton').exists()).toBe(true)
  })

  it('renders all four statistic cards correctly after data loaded', async () => {
    const wrapper = mount(OverviewCards)
    await flushPromises()

    const cards = wrapper.findAll('.stat-card')
    expect(cards.length).toBe(4)

    // 客户总数卡片
    expect(cards[0].text()).toContain('客户总数')
    expect(cards[0].text()).toContain('1320')
    expect(cards[0].text()).toContain('+5.2%')

    // 本月收入卡片
    expect(cards[1].text()).toContain('本月收入')
    expect(cards[1].text()).toContain('256,800')
    expect(cards[1].text()).toContain('+12.8%')

    // 待结算卡片
    expect(cards[2].text()).toContain('待结算')
    expect(cards[2].text()).toContain('89,500')
    expect(cards[2].text()).toContain('-3.5%')

    // 健康预警卡片
    expect(cards[3].text()).toContain('健康预警')
    expect(cards[3].text()).toContain('12')
    expect(cards[3].text()).toContain('+8.3%')
  })

  it('shows correct trend color (green for positive, red for negative)', async () => {
    const wrapper = mount(OverviewCards)
    await flushPromises()

    const cards = wrapper.findAll('.stat-card')
    
    // 正增长绿色
    expect(cards[0].find('.trend-positive').exists()).toBe(true)
    expect(cards[1].find('.trend-positive').exists()).toBe(true)
    expect(cards[3].find('.trend-positive').exists()).toBe(true)
    
    // 负增长红色
    expect(cards[2].find('.trend-negative').exists()).toBe(true)
  })

  it('navigates to correct page when card is clicked', async () => {
    const wrapper = mount(OverviewCards)
    await flushPromises()

    const cards = wrapper.findAll('.stat-card')
    
    // 客户总数跳转到客户列表
    await cards[0].trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/customers')

    // 本月收入跳转到结算列表
    await cards[1].trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/settlements?status=settled')

    // 待结算跳转到待结算列表
    await cards[2].trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/settlements?status=unsettled')

    // 健康预警跳转到健康度页面
    await cards[3].trigger('click')
    expect(routerPush).toHaveBeenCalledWith('/customers?health=warning')
  })

  it('shows error message when fetch fails', async () => {
    ;(dashboardApi.getOverview as vi.Mock).mockRejectedValue(new Error('Fetch failed'))
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    const wrapper = mount(OverviewCards)
    await flushPromises()

    expect(wrapper.find('.ant-empty-description').text()).toContain('加载失败')
    consoleErrorSpy.mockRestore()
  })
})