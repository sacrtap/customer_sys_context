<template>
  <a-card class="filter-card">
    <a-form :model="filters" layout="inline">
      <a-form-item label="行业">
        <a-select
          v-model:value="filters.industry_id"
          placeholder="请选择行业"
          style="width: 150px"
          data-testid="industry-filter"
          @change="handleFilterChange"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="1">房地产</a-select-option>
          <a-select-option value="2">金融</a-select-option>
          <a-select-option value="3">互联网</a-select-option>
          <a-select-option value="4">制造业</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="客户等级">
        <a-select
          v-model:value="filters.level_id"
          placeholder="请选择等级"
          style="width: 150px"
          data-testid="level-filter"
          @change="handleFilterChange"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="1">A级</a-select-option>
          <a-select-option value="2">B级</a-select-option>
          <a-select-option value="3">C级</a-select-option>
          <a-select-option value="4">D级</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="结算状态">
        <a-select
          v-model:value="filters.settlement_status"
          placeholder="请选择结算状态"
          style="width: 150px"
          data-testid="settlement-status-filter"
          @change="handleFilterChange"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="settled">已结算</a-select-option>
          <a-select-option value="unsettled">未结算</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="状态">
        <a-select
          v-model:value="filters.status"
          placeholder="请选择状态"
          style="width: 150px"
          data-testid="status-filter"
          @change="handleFilterChange"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="active">正常</a-select-option>
          <a-select-option value="inactive">停用</a-select-option>
          <a-select-option value="test">测试</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="负责人">
        <a-select
          v-model:value="filters.owner_id"
          placeholder="请选择负责人"
          style="width: 150px"
          data-testid="owner-filter"
          @change="handleFilterChange"
        >
          <a-select-option value="">全部</a-select-option>
          <a-select-option value="1">张三</a-select-option>
          <a-select-option value="2">李四</a-select-option>
          <a-select-option value="3">王五</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item>
        <a-space>
          <a-button type="primary" data-testid="search-btn" @click="handleSearch">
            <SearchOutlined />
            搜索
          </a-button>
          <a-button data-testid="reset-btn" @click="handleReset">
            <ReloadOutlined />
            重置
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'

interface Filters {
  industry_id?: string
  level_id?: string
  settlement_status?: string
  status?: string
  owner_id?: string
}

const props = defineProps<{
  filters?: Filters
}>()

const emit = defineEmits<{
  'update:filters': [filters: Filters]
  'search': [filters: Filters]
  'reset': []
}>()

const defaultFilters: Filters = {
  industry_id: '',
  level_id: '',
  settlement_status: '',
  status: '',
  owner_id: ''
}

const filters = reactive<Filters>({ ...defaultFilters, ...props.filters })

watch(() => props.filters, (newFilters) => {
  Object.assign(filters, { ...defaultFilters, ...newFilters })
}, { deep: true })

const handleFilterChange = () => {
  emit('update:filters', { ...filters })
}

const handleSearch = () => {
  emit('search', { ...filters })
}

const handleReset = () => {
  Object.assign(filters, defaultFilters)
  emit('reset')
  emit('search', { ...filters })
}
</script>

<style scoped>
.filter-card {
  margin-bottom: 16px;
}

:deep(.ant-form-inline .ant-form-item) {
  margin-bottom: 16px;
}
</style>
