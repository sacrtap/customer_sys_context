<template>
  <div class="settlement-list">
    <a-card>
      <div class="header-actions">
        <a-space>
          <a-button type="primary" @click="handleCreate">
            <template #icon><PlusOutlined /></template>
            新建结算
          </a-button>
          <a-button @click="handleGenerateBill">
            <template #icon><FileTextOutlined /></template>
            生成月度账单
          </a-button>
          <a-button @click="handleExport">
            <template #icon><DownloadOutlined /></template>
            导出结算
          </a-button>
        </a-space>
      </div>
      
      <SettlementFilter 
        @search="handleSearch" 
        @reset="handleReset" 
      />
      
      <a-divider />
      
      <a-table
        :columns="columns"
        :data-source="settlements"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'status'">
            <a-tag :color="record.status === 'settled' ? 'green' : 'orange'">
              {{ record.status === 'settled' ? '已结算' : '未结算' }}
            </a-tag>
          </template>
          
          <template v-if="column.key === 'amount'">
            ¥{{ record.amount.toLocaleString() }}
          </template>
          
          <template v-if="column.key === 'action'">
            <a-space size="small">
              <a @click="handleView(record)">详情</a>
              <a v-if="record.status === 'unsettled'" @click="handleConfirm(record)">
                确认支付
              </a>
              <a @click="handleDelete(record)" danger>删除</a>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
    
    <SettlementForm
      v-model:open="formVisible"
      :edit-data="editingSettlement"
      @success="handleFormSuccess"
    />
    
    <PaymentConfirmDialog
      v-model:open="paymentDialogVisible"
      :settlement="currentSettlement"
      @success="handlePaymentSuccess"
    />
    
    <GenerateBillDialog
      v-model:open="generateBillVisible"
      @success="handleGenerateSuccess"
    />
    
    <ExportSettlementDialog
      v-model:open="exportDialogVisible"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, FileTextOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import type { Settlement } from '@/api/settlement'
import { settlementApi } from '@/api/settlement'
import SettlementFilter from './components/SettlementFilter.vue'
import SettlementForm from './components/SettlementForm.vue'
import PaymentConfirmDialog from './components/PaymentConfirmDialog.vue'
import GenerateBillDialog from './components/GenerateBillDialog.vue'
import ExportSettlementDialog from './components/ExportSettlementDialog.vue'

const settlements = ref<Settlement[]>([])
const loading = ref(false)
const formVisible = ref(false)
const paymentDialogVisible = ref(false)
const generateBillVisible = ref(false)
const exportDialogVisible = ref(false)
const editingSettlement = ref<Settlement | null>(null)
const currentSettlement = ref<Settlement | null>(null)

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条记录`,
})

const filterParams = ref<Record<string, any>>({})

const columns = [
  {
    title: '客户名称',
    dataIndex: 'customer_name',
    key: 'customer_name',
    width: 200,
  },
  {
    title: '结算月份',
    dataIndex: 'month',
    key: 'month',
    width: 120,
  },
  {
    title: '结算金额',
    dataIndex: 'amount',
    key: 'amount',
    width: 150,
    align: 'right',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
  },
  {
    title: '结算时间',
    dataIndex: 'settled_at',
    key: 'settled_at',
    width: 180,
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
  },
  {
    title: '操作',
    key: 'action',
    width: 200,
    fixed: 'right',
  },
]

const fetchSettlements = async () => {
  loading.value = true
  try {
    const res = await settlementApi.getList({
      page: pagination.current,
      page_size: pagination.pageSize,
      ...filterParams.value,
    })
    settlements.value = res.items
    pagination.total = res.total
  } catch (err: any) {
    message.error('获取结算列表失败：' + err.message)
  } finally {
    loading.value = false
  }
}

const handleSearch = (params: Record<string, any>) => {
  filterParams.value = params
  pagination.current = 1
  fetchSettlements()
}

const handleReset = () => {
  filterParams.value = {}
  pagination.current = 1
  fetchSettlements()
}

const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchSettlements()
}

const handleCreate = () => {
  editingSettlement.value = null
  formVisible.value = true
}

const handleView = (record: Settlement) => {
  // 跳转到详情页
  window.location.href = `/settlements/${record.id}`
}

const handleConfirm = (record: Settlement) => {
  currentSettlement.value = record
  paymentDialogVisible.value = true
}

const handleDelete = (record: Settlement) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除 ${record.customer_name} 的结算记录吗？此操作不可恢复。`,
    onOk: async () => {
      try {
        await settlementApi.delete(record.id)
        message.success('删除成功')
        fetchSettlements()
      } catch (err: any) {
        message.error('删除失败：' + err.message)
      }
    },
  })
}

const handleFormSuccess = () => {
  formVisible.value = false
  message.success('保存成功')
  fetchSettlements()
}

const handlePaymentSuccess = () => {
  paymentDialogVisible.value = false
  message.success('支付确认成功')
  fetchSettlements()
}

const handleGenerateBill = () => {
  generateBillVisible.value = true
}

const handleGenerateSuccess = () => {
  generateBillVisible.value = false
  message.success('账单生成成功')
  fetchSettlements()
}

const handleExport = () => {
  exportDialogVisible.value = true
}

onMounted(() => {
  fetchSettlements()
})
</script>

<style scoped>
.settlement-list {
  padding: 24px;
}

.header-actions {
  margin-bottom: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
