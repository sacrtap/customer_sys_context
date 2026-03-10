<template>
  <div class="quick-actions" style="margin-top: 24px">
    <a-card title="快捷操作">
      <a-row :gutter="16">
        <a-col :span="6" v-for="action in actions" :key="action.name">
          <a-card
            class="action-card"
            hoverable
            data-testid="action-card"
            @click="handleActionClick(action.path)"
          >
            <div class="action-content">
              <component :is="action.icon" :style="`font-size: 32px; color: ${action.color}`" />
              <div class="action-title">{{ action.name }}</div>
              <div class="action-desc">{{ action.desc }}</div>
            </div>
          </a-card>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  TeamOutlined,
  FileTextOutlined,
  SafetyOutlined,
  CalendarOutlined
} from '@ant-design/icons-vue'

const router = useRouter()

const actions = [
  { 
    name: '客户管理', 
    desc: '管理客户信息和状态',
    icon: TeamOutlined,
    color: '#1890ff',
    path: '/customers' 
  },
  { 
    name: '用户管理', 
    desc: '管理系统用户账户',
    icon: FileTextOutlined,
    color: '#52c41a',
    path: '/users' 
  },
  { 
    name: '角色权限', 
    desc: '配置角色和权限',
    icon: SafetyOutlined,
    color: '#faad14',
    path: '/roles' 
  },
  { 
    name: '结算管理', 
    desc: '管理客户结算记录',
    icon: CalendarOutlined,
    color: '#722ed1',
    path: '/settlements' 
  },
]

const handleActionClick = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.action-card {
  text-align: center;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-content {
  padding: 20px 0;
}

.action-title {
  margin-top: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.action-desc {
  margin-top: 4px;
  font-size: 12px;
  color: #999;
}
</style>