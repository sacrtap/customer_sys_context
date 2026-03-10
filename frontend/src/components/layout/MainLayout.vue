<template>
  <a-layout class="main-layout">
    <a-layout-sider
      v-model:collapsed="collapsed"
      :trigger="null"
      collapsible
      class="sidebar"
      theme="light"
    >
      <div class="logo">
        <span v-if="!collapsed">客户运营中台</span>
        <span v-else>运营</span>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        :items="menuItems"
        @click="handleMenuClick"
      />
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header">
        <div class="header-left">
          <MenuUnfoldOutlined
            v-if="collapsed"
            class="trigger"
            @click="() => (collapsed = !collapsed)"
          />
          <MenuFoldOutlined v-else class="trigger" @click="() => (collapsed = !collapsed)" />
        </div>
        <div class="header-right">
          <a-dropdown>
            <span class="user-info">
              <a-avatar :size="32">
                <template #icon><UserOutlined /></template>
              </a-avatar>
              <span class="username">{{ authStore.user?.username || '用户' }}</span>
            </span>
            <template #overlay>
              <a-menu>
                <a-menu-item key="logout" @click="handleLogout">
                  <LogoutOutlined />
                  退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      <a-layout-content class="content">
        <RouterView />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup lang="ts">
import { ref, computed, h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { MenuProps } from 'ant-design-vue'
import {
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  UserOutlined,
  LogoutOutlined,
  DashboardOutlined,
  TeamOutlined,
  UsergroupAddOutlined,
  FileTextOutlined,
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const collapsed = ref(false)

const selectedKeys = computed(() => [route.path])

const handleMenuClick = ({ key }: { key: string }) => {
  router.push(key)
}

const menuItems = computed<MenuProps['items']>(() => [
  {
    key: '/dashboard',
    icon: () => h(DashboardOutlined),
    label: '工作台',
  },
  {
    key: '/customers',
    icon: () => h(TeamOutlined),
    label: '客户管理',
  },
  {
    key: '/users',
    icon: () => h(UsergroupAddOutlined),
    label: '用户管理',
  },
  {
    key: '/roles',
    icon: () => h(FileTextOutlined),
    label: '角色权限',
  },
])

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background: #fff;
  box-shadow: 2px 0 8px 0 rgba(0, 0, 0, 0.05);
  z-index: 10;
}

.logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  color: var(--primary-color);
  border-bottom: 1px solid #f0f0f0;
  transition: all 0.3s;
}

.header {
  background: #fff;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  height: var(--header-height);
  line-height: var(--header-height);
}

.header-left {
  display: flex;
  align-items: center;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  transition: color 0.3s;
}

.trigger:hover {
  color: var(--primary-color);
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: opacity 0.3s;
}

.user-info:hover {
  opacity: 0.8;
}

.username {
  margin-left: 8px;
  color: var(--text-primary);
}

.content {
  margin: var(--spacing-lg);
  padding: var(--spacing-lg);
  background: #fff;
  min-height: 280px;
  overflow: auto;
  flex: 1;
  border-radius: var(--border-radius-lg);
}

/* 响应式适配 */
@media (max-width: 768px) {
  .content {
    margin: var(--spacing-sm);
    padding: var(--spacing-md);
  }
  
  .header {
    padding: 0 16px;
  }
  
  .username {
    display: none;
  }
}
</style>
