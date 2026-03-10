<template>
  <div class="overview-cards">
    <a-row :gutter="16">
      <a-col :span="6" v-for="(card, index) in cards" :key="index">
        <a-card
          class="stat-card"
          :bordered="false"
          hoverable
          @click="handleCardClick(card.link)"
        >
          <a-skeleton :loading="loading" active>
            <a-statistic
              :title="card.title"
              :value="card.value"
              :value-style="{ color: card.color }"
              :precision="card.precision || 0"
            >
              <template #prefix>
                <component :is="card.icon" />
              </template>
              <template #suffix>
                <span v-if="card.unit" class="unit">{{ card.unit }}</span>
                <span
                  class="trend"
                  :class="{
                    'trend-positive': card.trend > 0,
                    'trend-negative': card.trend < 0
                  }"
                >
                  {{ card.trend > 0 ? '+' : '' }}{{ card.trend.toFixed(1) }}%
                </span>
              </template>
            </a-statistic>
          </a-skeleton>
        </a-card>
      </a-col>
    </a-row>

    <a-empty v-if="error" description="数据加载失败" style="margin: 40px 0" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  TeamOutlined,
  AccountBookOutlined,
  FileTextOutlined,
  WarningOutlined
} from '@ant-design/icons-vue'
import { dashboardApi, type OverviewData } from '@/api/dashboard'

const router = useRouter()

const loading = ref(true)
const error = ref(false)
const overviewData = ref<OverviewData | null>(null)

const cards = computed(() => {
  if (!overviewData.value) {
    return []
  }

  return [
    {
      title: '客户总数',
      value: overviewData.value.totalCustomers,
      color: '#3f8600',
      icon: TeamOutlined,
      unit: '户',
      precision: 0,
      trend: overviewData.value.trends.totalCustomers,
      link: '/customers'
    },
    {
      title: '本月收入',
      value: overviewData.value.monthlyRevenue,
      color: '#1890ff',
      icon: AccountBookOutlined,
      unit: '元',
      precision: 2,
      trend: overviewData.value.trends.monthlyRevenue,
      link: '/settlements?status=settled'
    },
    {
      title: '待结算',
      value: overviewData.value.pendingSettlement,
      color: '#faad14',
      icon: FileTextOutlined,
      unit: '元',
      precision: 2,
      trend: overviewData.value.trends.pendingSettlement,
      link: '/settlements?status=unsettled'
    },
    {
      title: '健康预警',
      value: overviewData.value.healthWarning,
      color: '#cf1322',
      icon: WarningOutlined,
      unit: '个',
      precision: 0,
      trend: overviewData.value.trends.healthWarning,
      link: '/customers?health=warning'
    }
  ]
})

const fetchData = async () => {
  loading.value = true
  error.value = false
  try {
    const res = await dashboardApi.getOverview()
    overviewData.value = res.data
  } catch (err) {
    console.error('Failed to fetch overview data:', err)
    error.value = true
  } finally {
    loading.value = false
  }
}

const handleCardClick = (link: string) => {
  router.push(link)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.stat-card {
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card :deep(.ant-statistic-title) {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-card :deep(.ant-statistic-content) {
  font-size: 28px;
  font-weight: 600;
}

.unit {
  font-size: 14px;
  color: #999;
  margin-left: 4px;
  font-weight: normal;
}

.trend {
  font-size: 12px;
  margin-left: 8px;
  font-weight: normal;
}

.trend-positive {
  color: #52c41a;
}

.trend-negative {
  color: #ff4d4f;
}
</style>