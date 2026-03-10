<template>
  <div class="customer-list page-container">
    <div class="table-card card-container">
      <div class="table-header">
        <div class="header-left">
          <a-space>
            <a-input-search
              v-model:value="searchValue"
              placeholder="搜索客户名称/编码/联系人"
              style="width: 300px"
              allow-clear
              @search="handleSearch"
              data-testid="search-input"
            />
            <a-button data-testid="reset-button" @click="handleReset">重置</a-button>
          </a-space>
        </div>
        <div class="header-right">
          <a-space>
            <a-button type="primary" data-testid="import-button" @click="handleImport">
              <UploadOutlined />
              导入客户
            </a-button>
            <a-button type="primary" data-testid="add-button" @click="handleAdd">
              <PlusOutlined />
              新建客户
            </a-button>
          </a-space>
        </div>
      </div>

      <a-table
        data-testid="customer-table"
        :columns="columns"
        :data-source="customers"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
        :scroll="{ x: 1200 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'customer_name'">
            <a data-testid="customer-name-link" @click="handleView(record)" class="customer-link">{{ record.customer_name }}</a>
          </template>
          <template v-if="column.key === 'status'">
            <a-badge
              :text="statusText(record.status)"
              :status="statusColor(record.status)"
            />
          </template>
          <template v-if="column.key === 'settlement_status'">
            <a-tag :color="record.settlement_status === 'settled' ? 'green' : 'orange'">
              {{ record.settlement_status === 'settled' ? '已结算' : '未结算' }}
            </a-tag>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a data-testid="view-button" @click="handleView(record)">查看</a>
              <a data-testid="edit-button" @click="handleEdit(record)">编辑</a>
              <a-popconfirm
                title="确定删除此客户吗？"
                @confirm="handleDelete(record)"
              >
                <a data-testid="delete-button" class="text-danger">删除</a>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- 客户表单对话框 -->
    <a-modal
      v-model:open="showForm"
      :title="editingCustomer ? '编辑客户' : '新建客户'"
      :footer="null"
      width="800px"
      data-testid="customer-form-modal"
      @cancel="showForm = false"
    >
      <CustomerForm
        :mode="editingCustomer ? 'edit' : 'create'"
        :customer="editingCustomer"
        :loading="formLoading"
        @submit="handleFormSubmit"
        @cancel="showForm = false"
      />
    </a-modal>

    <!-- 导入对话框 -->
    <a-modal
      v-model:open="importVisible"
      title="导入客户"
      :footer="null"
      data-testid="import-modal"
      @cancel="importVisible = false"
    >
      <a-upload-dragger
        v-model:file-list="fileList"
        :before-upload="beforeUpload"
        :show-upload-list="false"
        accept=".xlsx,.xls,.csv"
      >
        <p class="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p class="ant-upload-text">点击或拖拽文件到此处上传</p>
        <p class="ant-upload-hint">
          支持 Excel (.xlsx, .xls) 和 CSV 文件
        </p>
      </a-upload-dragger>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, h } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  PlusOutlined,
  UploadOutlined,
  InboxOutlined,
} from '@ant-design/icons-vue'
import type { ColumnsType } from 'ant-design-vue/es/table'
import type { UploadFile } from 'ant-design-vue'
import { request } from '@/api/request'
import CustomerForm from '@/components/customers/CustomerForm.vue'

interface Customer {
  id: string
  customer_code: string
  customer_name: string
  status: string
  settlement_status: string
  contact_person?: string
  contact_phone?: string
  industry?: { name: string }
  level?: { code: string; name: string }
  owner?: { username: string; full_name: string }
  created_at: string
}

interface CustomerListResponse {
  items: Customer[]
  total: number
}

const loading = ref(false)
const customers = ref<Customer[]>([])
const searchValue = ref('')
const importVisible = ref(false)
const fileList = ref<UploadFile[]>([])

// 表单相关
const showForm = ref(false)
const editingCustomer = ref<Customer | null>(null)
const formLoading = ref(false)

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const columns: ColumnsType<Customer> = [
  {
    title: '客户编码',
    dataIndex: 'customer_code',
    key: 'customer_code',
    width: 120,
    fixed: 'left',
  },
  {
    title: '客户名称',
    dataIndex: 'customer_name',
    key: 'customer_name',
    width: 200,
  },
  {
    title: '行业',
    dataIndex: ['industry', 'name'],
    key: 'industry',
    width: 120,
  },
  {
    title: '等级',
    dataIndex: ['level', 'code'],
    key: 'level',
    width: 80,
  },
  {
    title: '联系人',
    dataIndex: 'contact_person',
    key: 'contact_person',
    width: 100,
  },
  {
    title: '联系电话',
    dataIndex: 'contact_phone',
    key: 'contact_phone',
    width: 130,
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 80,
  },
  {
    title: '结算状态',
    dataIndex: 'settlement_status',
    key: 'settlement_status',
    width: 90,
  },
  {
    title: '负责人',
    dataIndex: ['owner', 'full_name'],
    key: 'owner',
    width: 100,
  },
  {
    title: '操作',
    key: 'action',
    width: 180,
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

const fetchCustomers = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.current,
      page_size: pagination.pageSize,
    }
    if (searchValue.value) {
      params.search = searchValue.value
    }

    const response = await request.get<CustomerListResponse>('/customers', { params })
    customers.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    console.error('获取客户列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  fetchCustomers()
}

const handleReset = () => {
  searchValue.value = ''
  pagination.current = 1
  fetchCustomers()
}

const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchCustomers()
}

const handleAdd = () => {
  editingCustomer.value = null
  showForm.value = true
}

const handleView = (record: Customer) => {
  message.info(`查看客户：${record.customer_name}`)
}

const handleEdit = (record: Customer) => {
  editingCustomer.value = record
  showForm.value = true
}

const handleDelete = (record: Customer) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除客户"${record.customer_name}"吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      try {
        await request.delete(`/customers/${record.id}`)
        message.success('客户删除成功')
        await fetchCustomers()
      } catch (error) {
        console.error('删除客户失败:', error)
        message.error('删除客户失败')
      }
    },
  })
}

const handleFormSubmit = async (data: Customer) => {
  formLoading.value = true
  try {
    if (editingCustomer.value) {
      await request.put(`/customers/${editingCustomer.value.id}`, data)
      message.success('客户更新成功')
    } else {
      await request.post('/customers', data)
      message.success('客户创建成功')
    }
    showForm.value = false
    await fetchCustomers()
  } catch (error) {
    console.error('保存客户失败:', error)
    message.error('保存客户失败')
  } finally {
    formLoading.value = false
  }
}

const handleImport = () => {
  importVisible.value = true
}

const beforeUpload = (file: UploadFile) => {
  console.log('上传文件:', file)
  message.success(`文件 ${file.name} 上传成功，待实现导入逻辑`)
  importVisible.value = false
  return false
}

onMounted(() => {
  fetchCustomers()
})
</script>

<style scoped>
.customer-list {
  height: 100%;
  overflow: auto;
}

.table-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 300px;
}

.header-right {
  display: flex;
  align-items: center;
}

.customer-link {
  color: var(--primary-color);
  cursor: pointer;
  transition: color 0.3s;
}

.customer-link:hover {
  color: var(--primary-hover);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-left,
  .header-right {
    width: 100%;
    justify-content: flex-start;
  }
  
  .header-right {
    margin-top: var(--spacing-sm);
  }
}
</style>
