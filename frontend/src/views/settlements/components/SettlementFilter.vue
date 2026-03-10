<template>
  <div class="settlement-filter">
    <a-form layout="inline" :model="filters">
      <a-form-item label="客户">
        <a-select
          v-model:value="filters.customer_id"
          placeholder="请选择客户"
          style="width: 200px"
          allow-clear
        >
          <a-select-option v-for="customer in customers" :key="customer.id" :value="customer.id">
            {{ customer.name }}
          </a-select-option>
        </a-select>
      </a-form-item>
      
      <a-form-item label="状态">
        <a-select
          v-model:value="filters.status"
          placeholder="请选择状态"
          style="width: 120px"
          allow-clear
        >
          <a-select-option value="unsettled">未结算</a-select-option>
          <a-select-option value="settled">已结算</a-select-option>
        </a-select>
      </a-form-item>
      
      <a-form-item label="月份">
        <a-month-picker
          v-model:value="filters.month"
          placeholder="请选择月份"
          style="width: 180px"
          format="YYYY-MM"
          value-format="YYYY-MM"
          allow-clear
        />
      </a-form-item>
      
      <a-form-item>
        <a-space>
          <a-button type="primary" @click="handleSearch">
            <template #icon><SearchOutlined /></template>
            搜索
          </a-button>
          <a-button @click="handleReset">
            <template #icon><ReloadOutlined /></template>
            重置
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { customerApi } from '@/api/customer'

interface CustomerOption {
  id: string
  name: string
}

const emit = defineEmits<{
  search: [params: Record<string, any>]
  reset: []
}>()

const filters = reactive<{
  customer_id?: string
  status?: string
  month?: string
}>({})

const customers = ref<CustomerOption[]>([])

const fetchCustomers = async () => {
  try {
    const res = await customerApi.getList({ page_size: 1000 })
    customers.value = res.items.map((item: any) => ({
      id: item.id,
      name: item.name
    }))
  } catch (err) {
    console.error('获取客户列表失败', err)
  }
}

const handleSearch = () => {
  const params = { ...filters }
  // 移除空值
  (Object.keys(params) as Array<keyof typeof params>).forEach(key => {
    if (params[key] === undefined || params[key] === null || params[key] === '') {
      delete params[key]
    }
  })
  emit('search', params)
}

const handleReset = () => {
  Object.keys(filters).forEach(key => {
    filters[key as keyof typeof filters] = undefined
  })
  emit('reset')
  emit('search', {})
}

onMounted(() => {
  fetchCustomers()
})
</script>

<style scoped>
.settlement-filter {
  padding: 16px 0;
}
</style>
