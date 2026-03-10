<template>
  <div class="dashboard">
    <!-- 概览卡片 -->
    <OverviewCards />
    
    <!-- 图表区域 -->
    <a-row :gutter="[16, 16]" style="margin-top: 24px">
      <a-col :xs="24" :sm="12">
        <a-card title="用量趋势" size="small" :bordered="false">
          <UsageTrendChart />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12">
        <a-card title="收入预测" size="small" :bordered="false">
          <RevenueForecastChart />
        </a-card>
      </a-col>
    </a-row>
    
    <a-row :gutter="[16, 16]" style="margin-top: 16px">
      <a-col :xs="24" :sm="12">
        <a-card title="客户分布" size="small" :bordered="false">
          <CustomerDistributionChart />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12">
        <a-card title="结算状态" size="small" :bordered="false">
          <SettlementStatusChart />
        </a-card>
      </a-col>
    </a-row>
    
    <!-- 快捷操作 -->
    <QuickActions />
  </div>
</template>

<script setup lang="ts">
import OverviewCards from '@/components/dashboard/OverviewCards.vue'
import QuickActions from '@/components/dashboard/QuickActions.vue'
import UsageTrendChart from '@/components/charts/UsageTrendChart.vue'
import RevenueForecastChart from '@/components/charts/RevenueForecastChart.vue'
import CustomerDistributionChart from '@/components/charts/CustomerDistributionChart.vue'
import SettlementStatusChart from '@/components/charts/SettlementStatusChart.vue'
</script>

<style scoped>
.dashboard {
  padding: 0;
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

/* 响应式适配 */
@media (max-width: 768px) {
  .dashboard {
    padding: 0;
  }
}
</style>
