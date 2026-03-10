<template>
  <div class="customer-distribution-chart">
    <a-card class="chart-card">
      <template #title>
        <div class="chart-header">
          <span>客户分布</span>
          <a-space>
            <a-radio-group v-model:value="dimension" button-style="solid" @change="handleDimensionChange">
              <a-radio-button value="industry">按行业</a-radio-button>
              <a-radio-button value="level">按等级</a-radio-button>
            </a-radio-group>
            <a-select v-model:value="chartType" style="width: 100px" @change="handleChartTypeChange">
              <a-select-option value="pie">饼图</a-select-option>
              <a-select-option value="ring">环形图</a-select-option>
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
import { PieChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// 注册ECharts组件
use([
  CanvasRenderer,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent
])

// 数据类型定义
export interface CustomerDistributionData {
  name: string
  value: number
  percentage: number
}

// Props定义
interface Props {
  data?: CustomerDistributionData[]
  loading?: boolean
  dimension?: 'industry' | 'level'
  chartType?: 'pie' | 'ring'
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false,
  dimension: 'industry',
  chartType: 'ring'
})

// Emits定义
const emit = defineEmits<{
  dimensionChange: [dimension: 'industry' | 'level']
  chartTypeChange: [type: 'pie' | 'ring']
}>()

// 内部状态
const dimension = ref(props.dimension)
const chartType = ref(props.chartType)

// 处理维度切换
const handleDimensionChange = (value: 'industry' | 'level') => {
  dimension.value = value
  emit('dimensionChange', value)
}

// 处理图表类型切换
const handleChartTypeChange = (value: 'pie' | 'ring') => {
  chartType.value = value
  emit('chartTypeChange', value)
}

// 计算图表配置
const chartOption = computed(() => {
  if (!props.data || props.data.length === 0) {
    return {}
  }

  const titleText = dimension.value === 'industry' ? '客户行业分布' : '客户等级分布'

  const radius = chartType.value === 'ring' ? ['40%', '70%'] : '70%'

  return {
    title: {
      text: titleText,
      left: 'center',
      top: 10
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'center'
    },
    series: [
      {
        name: titleText,
        type: 'pie',
        radius: radius,
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: true
        },
        data: props.data.map(item => ({
          name: item.name,
          value: item.value
        }))
      }
    ]
  }
})

// 对外暴露方法供测试使用
defineExpose({
  handleDimensionChange,
  chartOption
})
</script>

<style scoped>
.customer-distribution-chart {
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
