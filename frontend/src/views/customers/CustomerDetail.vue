<template>
  <a-spin :spinning="pageLoading" tip="加载中...">
    <div class="customer-detail page-container">
      <div class="detail-card card-container">
        <a-page-header
          title="客户详情"
          @back="$router.back()"
        >
          <template #extra>
            <a-space>
              <a-button @click="handleEdit">编辑</a-button>
              <a-button @click="handleExportUsage">导出用量</a-button>
              <a-button type="primary" @click="$router.back()">返回列表</a-button>
            </a-space>
          </template>
        </a-page-header>

        <a-descriptions
          title="基本信息"
          bordered
          :column="{ xxl: 2, xl: 2, lg: 2, md: 2, sm: 1, xs: 1 }"
          class="detail-section"
          size="small"
        >
          <a-descriptions-item label="客户编码">{{ customer.customer_code }}</a-descriptions-item>
          <a-descriptions-item label="客户名称">{{ customer.customer_name }}</a-descriptions-item>
          <a-descriptions-item label="行业">{{ customer.industry?.name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="客户等级">{{ customer.level?.name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-badge
              :text="statusText(customer.status)"
              :status="statusColor(customer.status)"
            />
          </a-descriptions-item>
          <a-descriptions-item label="结算状态">
            <a-tag :color="customer.settlement_status === 'settled' ? 'green' : 'orange'">
              {{ customer.settlement_status === 'settled' ? '已结算' : '未结算' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="联系人">{{ customer.contact_person || '-' }}</a-descriptions-item>
          <a-descriptions-item label="联系电话">{{ customer.contact_phone || '-' }}</a-descriptions-item>
          <a-descriptions-item label="联系邮箱" :span="2">{{ customer.contact_email || '-' }}</a-descriptions-item>
          <a-descriptions-item label="地址" :span="2">{{ customer.address || '-' }}</a-descriptions-item>
          <a-descriptions-item label="负责人">{{ customer.owner?.full_name || '-' }}</a-descriptions-item>
          <a-descriptions-item label="创建时间">{{ customer.created_at }}</a-descriptions-item>
          <a-descriptions-item label="备注" :span="2">{{ customer.remark || '-' }}</a-descriptions-item>
        </a-descriptions>

        <!-- 用量趋势图表 -->
        <div class="detail-section">
          <a-card title="用量趋势" size="small" :bordered="false">
            <UsageTrendChart
              :data="usageTrendData"
              :loading="usageLoading"
              chart-type="bar"
              @date-range-change="handleDateRangeChange"
            />
          </a-card>
        </div>

        <!-- 结算记录表格 -->
        <div class="detail-section">
          <a-card title="结算记录" size="small" :bordered="false">
            <a-table
              :columns="settlementColumns"
              :data-source="settlementRecords"
              :loading="settlementLoading"
              :pagination="settlementPagination"
              row-key="id"
              @change="handleSettlementTableChange"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'status'">
                  <a-tag :color="record.status === 'settled' ? 'green' : 'orange'">
                    {{ record.status === 'settled' ? '已结算' : '未结算' }}
                  </a-tag>
                </template>
                <template v-if="column.key === 'amount'">
                  <span class="amount-text">¥{{ record.amount.toFixed(2) }}</span>
                </template>
                <template v-if="column.key === 'action'">
                  <a-space>
                    <a v-if="record.status === 'unsettled'" @click="handleSettlementPay(record)">结算</a>
                    <a @click="handleViewSettlement(record)">查看详情</a>
                  </a-space>
                </template>
              </template>
            </a-table>
          </a-card>
        </div>
      </div>
    </div>
  </a-spin>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, type ColumnsType } from 'ant-design-vue'
import { request } from '@/api/request'
import UsageTrendChart, { type UsageTrendData } from '@/components/charts/UsageTrendChart.vue'

const route = useRoute()
const router = useRouter()

interface Customer {
  id: string
  customer_code: string
  customer_name: string
  industry?: { name: string }
  level?: { name: string; code: string }
  status: string
  settlement_status: string
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  address?: string
  owner?: { full_name: string }
  remark?: string
  created_at: string
}

interface SettlementRecord {
  id: string
  month: string
  amount: number
  status: 'settled' | 'unsettled'
  created_at: string
  paid_at?: string
}

const pageLoading = ref(true)
const customer = ref<Customer>({} as Customer)
const usageLoading = ref(false)
const usageTrendData = ref<UsageTrendData[]>([])
const settlementLoading = ref(false)
const settlementRecords = ref<SettlementRecord[]>([])
const settlementPagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const settlementColumns: ColumnsType<SettlementRecord> = [
  {
    title: '月份',
    dataIndex: 'month',
    key: 'month',
    width: 120,
  },
  {
    title: '金额',
    dataIndex: 'amount',
    key: 'amount',
    width: 120,
    align: 'right',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 160,
  },
  {
    title: '结算时间',
    dataIndex: 'paid_at',
    key: 'paid_at',
    width: 160,
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    fixed: 'right',
  },
]

const statusText = (status: string) => {
  const map: Record<string, string> = {
    active: '正常',
    inactive: '停用',
    test: '测试',
  }
  return map[status] || status
}

const statusColor = (status: string) => {
  const map: Record<string, 'success' | 'default' | 'error'> = {
    active: 'success',
    inactive: 'default',
    test: 'default',
  }
  return map[status] || 'default'
}

const fetchCustomer = async () => {
  try {
    const response = await request.get(`/customers/${route.params.id}`)
    customer.value = response
  } catch (error) {
    message.error('获取客户详情失败')
  }
}

const fetchUsageTrend = async (startDate?: string, endDate?: string) => {
  usageLoading.value = true
  try {
    const params: Record<string, any> = {
      customer_id: route.params.id,
      range: '12m'
    }
    if (startDate && endDate) {
      params.start_date = startDate
      params.end_date = endDate
    }
    const response = await request.get(`/customers/${route.params.id}/usage-trend`, { params })
    usageTrendData.value = response.items || []
  } catch (error) {
    message.error('获取用量趋势失败')
  } finally {
    usageLoading.value = false
  }
}

const fetchSettlementRecords = async () => {
  settlementLoading.value = true
  try {
    const params: Record<string, any> = {
      customer_id: route.params.id,
      page: settlementPagination.current,
      page_size: settlementPagination.pageSize,
    }
    const response = await request.get(`/settlements`, { params })
    settlementRecords.value = response.items || []
    settlementPagination.total = response.total || 0
  } catch (error) {
    message.error('获取结算记录失败')
  } finally {
    settlementLoading.value = false
  }
}

const handleEdit = () => {
  message.info('编辑功能待实现')
}

const handleExportUsage = async () => {
  try {
    const response = await request.get(`/customers/${route.params.id}/export-usage`, {
      responseType: 'blob'
    })
    const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${customer.value.customer_name}_用量记录.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
  }
}

const handleDateRangeChange = (range: [string, string]) => {
  fetchUsageTrend(range[0], range[1])
}

const handleSettlementTableChange = (pag: any) => {
  settlementPagination.current = pag.current
  settlementPagination.pageSize = pag.pageSize
  fetchSettlementRecords()
}

const handleSettlementPay = (record: SettlementRecord) => {
  message.info(`结算功能待实现：${record.month}`)
}

const handleViewSettlement = (record: SettlementRecord) => {
  router.push(`/settlements/${record.id}`)
}

const initPage = async () => {
  const customerId = route.params.id
  if (!customerId || Array.isArray(customerId)) {
    message.error('客户 ID 无效')
    router.back()
    return
  }

  pageLoading.value = true
  try {
    await Promise.all([
      fetchCustomer(),
      fetchUsageTrend(),
      fetchSettlementRecords()
    ])
  } finally {
    pageLoading.value = false
  }
}

onMounted(() => {
  initPage()
})
</script>

<style scoped>
.customer-detail {
  height: 100%;
  overflow: auto;
}

.detail-card {
  min-height: 100%;
}

.detail-section {
  margin-top: var(--spacing-lg);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.amount-text {
  font-weight: 500;
  color: var(--text-primary);
}

/* 响应式适配 */
@media screen and (max-width: 768px) {
  .detail-section {
    margin-top: var(--spacing-md);
  }

  :deep(.ant-descriptions) {
    font-size: var(--font-size-sm);
  }

  :deep(.ant-descriptions-item) {
    padding: 8px !important;
  }

  :deep(.ant-page-header-heading-extra) {
    flex-wrap: wrap;
    gap: var(--spacing-xs);
  }
  
  :deep(.ant-page-header-heading-extra .ant-btn) {
    padding: 4px 8px;
    font-size: var(--font-size-sm);
  }
}
</style>
