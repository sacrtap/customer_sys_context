<template>
  <div class="settlement-status-chart">
    <a-card class="chart-card">
      <template #title>
        <div class="chart-header">
          <span>结算状态</span>
          <a-space>
            <a-statistic title="已结算总额" :value="totalSettled" :precision="0" suffix="元" />
            <a-statistic title="未结算总额" :value="totalUnsettled" :precision="0" suffix="元" />
            <a-select v-model:value="viewType" style="width: 120px" @change="handleViewTypeChange">
              <a-select-option value="monthly">月度</a-select-option>
              <a-select-option value="annual">年度汇总</a-select-option>
            </a-select>
          </a-space>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <a-spin size="large" />
      </div>

      <div v-else-if="!data || data.length === 0" class="empty-state">
        <a-empty description="暂无数据" />
      </div>

      <div v-else class="chart-container">
        <v-chart :option="chartOption" autoresize />
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// 注册ECharts组件
use([
  CanvasRenderer,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
])

// 数据类型定义
export interface SettlementStatusData {
  month: string
  settled: number
  unsettled: number
}

// Props定义
interface Props {
  data?: SettlementStatusData[]
  loading?: boolean
  viewType?: 'monthly' | 'annual'
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false,
  viewType: 'monthly'
})

// Emits定义
const emit = defineEmits<{
  viewTypeChange: [type: 'monthly' | 'annual']
}>()

// 内部状态
const viewType = ref(props.viewType)

// 计算统计数据
const totalSettled = computed(() => {
  return props.data.reduce((sum, item) => sum + item.settled, 0)
})

const totalUnsettled = computed(() => {
  return props.data.reduce((sum, item) => sum + item.unsettled, 0)
})

// 处理视图类型变化
const handleViewTypeChange = (value: 'monthly' | 'annual') => {
  viewType.value = value
  emit('viewTypeChange', value)
}

// 计算图表配置
const chartOption = computed(() => {
  if (!props.data || props.data.length === 0) {
    return {}
  }

  const months = props.data.map(item => item.month)
  const settledData = props.data.map(item => item.settled)
  const unsettledData = props.data.map(item => item.unsettled)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const param = params[0]
        const data = props.data[param.dataIndex]
        if (!data) return param.name
        return `${param.name}<br/>
          已结算: ${data.settled.toLocaleString()} 元<br/>
          未结算: ${data.unsettled.toLocaleString()} 元<br/>
          合计: ${(data.settled + data.unsettled).toLocaleString()} 元`
      }
    },
    legend: {
      data: ['已结算', '未结算'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '金额(元)'
    },
    dataZoom: [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '已结算',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: settledData,
        itemStyle: {
          color: '#52c41a'
        }
      },
      {
        name: '未结算',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: unsettledData,
        itemStyle: {
          color: '#faad14'
        }
      }
    ]
  }
})

// 对外暴露方法供测试使用
defineExpose({
  handleViewTypeChange,
  totalSettled,
  totalUnsettled,
  chartOption
})
</script>

<style scoped>
.settlement-status-chart {
  width: 100%;
}

.chart-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.ant-statistic) {
  display: inline-block;
  margin-right: 32px;
}

:deep(.ant-statistic-title) {
  font-size: 12px;
  margin-bottom: 4px;
}

:deep(.ant-statistic-content) {
  font-size: 18px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 20px;
}
</style>
