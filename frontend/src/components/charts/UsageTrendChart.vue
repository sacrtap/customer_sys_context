<template>
  <div class="usage-trend-chart">
    <a-card class="chart-card">
      <template #title>
        <div class="chart-header">
          <span>用量趋势</span>
          <a-space>
            <a-select
              v-model:value="selectedRange"
              style="width: 120px"
              @change="handleRangeChange"
            >
              <a-select-option value="7d">近7天</a-select-option>
              <a-select-option value="30d">近30天</a-select-option>
              <a-select-option value="90d">近90天</a-select-option>
              <a-select-option value="custom">自定义</a-select-option>
            </a-select>
            <a-range-picker
              v-if="selectedRange === 'custom'"
              v-model:value="customDateRange"
              @change="handleCustomRangeChange"
            />
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
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DataZoomComponent
])

// 数据类型定义
export interface UsageTrendData {
  date: string
  usageCount: number
  amount: number
  [key: string]: any
}

// Props定义
interface Props {
  data?: UsageTrendData[]
  loading?: boolean
  dateRange?: [string, string]
  compareMode?: boolean
  chartType?: 'line' | 'bar' | 'mixed'
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  loading: false,
  compareMode: false,
  chartType: 'mixed'
})

// Emits定义
const emit = defineEmits<{
  dateRangeChange: [range: [string, string]]
}>()

// 内部状态
const selectedRange = ref<string>('30d')
const customDateRange = ref<[dayjs.Dayjs, dayjs.Dayjs] | null>(null)

// 处理时间范围切换
const handleRangeChange = (value: string) => {
  let endDate = dayjs()
  let startDate: dayjs.Dayjs

  switch (value) {
    case '7d':
      startDate = endDate.subtract(6, 'day')
      break
    case '30d':
      startDate = endDate.subtract(29, 'day')
      break
    case '90d':
      startDate = endDate.subtract(89, 'day')
      break
    default:
      return
  }

  const range: [string, string] = [startDate.format('YYYY-MM-DD'), endDate.format('YYYY-MM-DD')]
  emit('dateRangeChange', range)
}

// 处理自定义时间范围
const handleCustomRangeChange = (dates: any) => {
  if (dates && dates.length === 2) {
    const range: [string, string] = [
      dates[0].format('YYYY-MM-DD'),
      dates[1].format('YYYY-MM-DD')
    ]
    emit('dateRangeChange', range)
  }
}

// 对外暴露方法供测试使用
const handleDateRangeChange = (range: [string, string]) => {
  emit('dateRangeChange', range)
}

// 计算图表配置
const chartOption = computed(() => {
  if (!props.data || props.data.length === 0) {
    return {}
  }

  const dates = props.data.map(item => item.date)

  let series = []
  let legendData = []

  if (props.compareMode) {
    // 多客户对比模式
    const keys = Object.keys(props.data[0]!).filter(key => key !== 'date')
    legendData = keys
    series = keys.map(key => ({
      name: key,
      type: 'line',
      smooth: true,
      data: props.data.map(item => item[key])
    }))
  } else {
    // 普通模式
    legendData = ['使用量', '消费金额']
    if (props.chartType === 'line') {
      series = [
        {
          name: '使用量',
          type: 'line',
          smooth: true,
          yAxisIndex: 0,
          data: props.data.map(item => item.usageCount)
        },
        {
          name: '消费金额',
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          data: props.data.map(item => item.amount)
        }
      ]
    } else if (props.chartType === 'bar') {
      series = [
        {
          name: '使用量',
          type: 'bar',
          yAxisIndex: 0,
          data: props.data.map(item => item.usageCount)
        },
        {
          name: '消费金额',
          type: 'bar',
          yAxisIndex: 1,
          data: props.data.map(item => item.amount)
        }
      ]
    } else {
      // 混合模式
      series = [
        {
          name: '使用量',
          type: 'bar',
          yAxisIndex: 0,
          data: props.data.map(item => item.usageCount)
        },
        {
          name: '消费金额',
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          data: props.data.map(item => item.amount)
        }
      ]
    }
  }

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: legendData,
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
      boundaryGap: props.chartType === 'line' ? false : true,
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '使用量',
        position: 'left'
      },
      {
        type: 'value',
        name: '金额(元)',
        position: 'right'
      }
    ],
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
    series
  }
})

// 对外暴露方法供测试使用
defineExpose({
  handleDateRangeChange,
  chartOption
})
</script>

<style scoped>
.usage-trend-chart {
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
