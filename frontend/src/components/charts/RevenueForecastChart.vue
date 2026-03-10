<template>
  <div class="revenue-forecast-chart">
    <a-card class="chart-card">
      <template #title>
        <div class="chart-header">
          <span>收入预测</span>
          <a-select
            v-model:value="forecastPeriod"
            style="width: 120px"
            @change="handlePeriodChange"
          >
            <a-select-option value="1m">1个月</a-select-option>
            <a-select-option value="3m">3个月</a-select-option>
            <a-select-option value="6m">6个月</a-select-option>
          </a-select>
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
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkAreaComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkAreaComponent
])

// 数据类型定义
export interface RevenueForecastData {
  month: string
  actual: number
  forecast: number
  lowerBound: number
  upperBound: number
}

// Props定义
interface Props {
  data?: RevenueForecastData[]
  loading?: boolean
  forecastPeriod?: '1m' | '3m' | '6m'
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false,
  forecastPeriod: '3m'
})

// Emits定义
const emit = defineEmits<{
  periodChange: [period: '1m' | '3m' | '6m']
}>()

// 内部状态
const forecastPeriod = ref(props.forecastPeriod)

// 处理预测周期变化
const handlePeriodChange = (value: '1m' | '3m' | '6m') => {
  forecastPeriod.value = value
  emit('periodChange', value)
}

// 计算图表配置
const chartOption = computed(() => {
  if (!props.data || props.data.length === 0) {
    return {}
  }

  const months = props.data.map(item => item.month)
  const actualData = props.data.map(item => item.actual || null)
  const forecastData = props.data.map(item => item.forecast || null)
  const lowerBoundData = props.data.map(item => item.lowerBound || null)
  const upperBoundData = props.data.map(item => item.upperBound || null)

  // 找到预测开始的索引（暂时未使用）
  // const forecastStartIndex = props.data.findIndex(item => item.forecast > 0)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params: any) => {
        const param = params[0]
        const data = props.data[param.dataIndex]
        if (!data) return param.name
        let result = `${param.name}<br/>`
        if (data.actual > 0) {
          result += `实际收入: ${data.actual.toLocaleString()} 元<br/>`
        }
        if (data.forecast > 0) {
          result += `预测收入: ${data.forecast.toLocaleString()} 元<br/>`
          result += `置信区间: ${data.lowerBound.toLocaleString()} - ${data.upperBound.toLocaleString()} 元`
        }
        return result
      }
    },
    legend: {
      data: ['实际收入', '预测收入'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: months
    },
    yAxis: {
      type: 'value',
      name: '金额(元)'
    },
    series: [
      {
        name: '实际收入',
        type: 'line',
        smooth: true,
        lineStyle: {
          width: 3
        },
        data: actualData
      },
      {
        name: '预测收入',
        type: 'line',
        smooth: true,
        lineStyle: {
          width: 3,
          type: 'dashed'
        },
        data: forecastData
      },
      {
        name: '置信区间',
        type: 'line',
        data: upperBoundData,
        lineStyle: {
          width: 0
        },
        stack: 'confidence',
        symbol: 'none',
        itemStyle: {
          color: 'rgba(255, 70, 131, 0)'
        },
        areaStyle: {
          color: 'rgba(255, 70, 131, 0.2)'
        }
      },
      {
        name: '置信区间',
        type: 'line',
        data: lowerBoundData,
        lineStyle: {
          width: 0
        },
        stack: 'confidence',
        symbol: 'none',
        itemStyle: {
          color: 'rgba(255, 70, 131, 0)'
        },
        label: {
          show: false
        }
      }
    ]
  }
})

// 对外暴露方法供测试使用
defineExpose({
  handlePeriodChange,
  chartOption
})
</script>

<style scoped>
.revenue-forecast-chart {
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
