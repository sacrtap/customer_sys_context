<template>
  <div class="user-list page-container">
    <div class="table-card card-container">
      <div class="table-header">
        <div class="header-left">
          <a-space>
          <a-input-search
            v-model:value="searchValue"
            placeholder="搜索用户名/姓名/邮箱"
            style="width: 300px"
            allow-clear
            data-testid="search-input"
            @search="handleSearch"
          />
          <a-button @click="handleReset" data-testid="reset-button">重置</a-button>
          </a-space>
        </div>
        <div class="header-right">
          <a-button type="primary" data-testid="add-user-btn" @click="handleAdd">
            <PlusOutlined />
            新建用户
          </a-button>
        </div>
      </div>

      <a-table
        :columns="columns"
        :data-source="users"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="id"
        :scroll="{ x: 1000 }"
        data-testid="user-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'username'">
            <a-space>
              <a-avatar :size="24">
                <template #icon><UserOutlined /></template>
              </a-avatar>
              {{ record.username }}
            </a-space>
          </template>
          <template v-if="column.key === 'is_active'">
            <a-badge
              :text="record.is_active ? '正常' : '禁用'"
              :status="record.is_active ? 'success' : 'error'"
            />
          </template>
          <template v-if="column.key === 'roles'">
            <a-space :size="4">
              <a-tag v-for="role in record.roles" :key="role.id" color="blue">
                {{ role.name }}
              </a-tag>
            </a-space>
          </template>
           <template v-if="column.key === 'action'">
             <a-space>
               <a data-testid="edit-user-btn" @click="handleEdit(record)">编辑</a>
               <a class="text-danger" data-testid="delete-user-btn" @click="showDeleteConfirm(record)">删除</a>
             </a-space>
           </template>
        </template>
      </a-table>
    </div>

    <a-modal
      v-model:open="formVisible"
      :title="editingUserId ? '编辑用户' : '新建用户'"
      :footer="null"
      width="600px"
      destroyOnClose
    >
      <UserForm
        v-if="formVisible"
        :mode="editingUserId ? 'edit' : 'create'"
        :user="getEditingUser()"
        :role-list="roles"
        :loading="formLoading"
        @submit="handleFormSubmit"
        @cancel="formVisible = false"
      />
    </a-modal>

     <!-- 删除确认弹窗 -->
     <a-modal
       v-model:open="deleteVisible"
       title="确认删除"
       ok-text="删除"
       cancel-text="取消"
       ok-type="danger"
       @ok="handleDelete"
       @cancel="deleteVisible = false"
     >
       <p>确定要删除 <strong>{{ deletingUser?.username }}</strong> 吗？</p>
       <a-alert
         type="warning"
         message="此操作不可恢复，请谨慎操作！"
         class="mt-3"
       />
     </a-modal>
   </div>
 </template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, UserOutlined } from '@ant-design/icons-vue'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { request } from '@/api/request'
import { handleError } from '@/utils/error'
import UserForm from '@/components/users/UserForm.vue'
import type { UserFormData } from '@/components/users/UserForm.vue'

interface User {
  id: string
  username: string
  email: string
  full_name?: string
  phone?: string
  is_active: boolean
  roles: Array<{ id: string; name: string }>
  created_at: string
}

const loading = ref(false)
const users = ref<User[]>([])
const searchValue = ref('')
const formVisible = ref(false)
const formLoading = ref(false)
const editingUserId = ref<string | null>(null)
const deleteVisible = ref(false)
const deletingUser = ref<User | null>(null)
const roles = ref<Array<{ id: string; name: string }>>([])

const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const columns: ColumnsType<User> = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    width: 180,
    fixed: 'left',
  },
  {
    title: '姓名',
    dataIndex: 'full_name',
    key: 'full_name',
    width: 100,
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
    width: 200,
  },
  {
    title: '电话',
    dataIndex: 'phone',
    key: 'phone',
    width: 130,
  },
  {
    title: '角色',
    dataIndex: 'roles',
    key: 'roles',
    width: 200,
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    key: 'is_active',
    width: 80,
  },
  {
    title: '创建时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 160,
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    fixed: 'right',
  },
]

const fetchUsers = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.current,
      page_size: pagination.pageSize,
    }
    if (searchValue.value) {
      params.search = searchValue.value
    }

    const response = await request.get('/users', { params })
    users.value = response.items || []
    pagination.total = response.total || 0
  } catch (error) {
    handleError(error, '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  fetchUsers()
}

const handleReset = () => {
  searchValue.value = ''
  pagination.current = 1
  fetchUsers()
}

const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchUsers()
}

const handleAdd = () => {
  editingUserId.value = null
  formVisible.value = true
}

const handleEdit = (record: User) => {
  editingUserId.value = record.id
  formVisible.value = true
}

const getEditingUser = () => {
  if (!editingUserId.value) return undefined
  return users.value.find(u => u.id === editingUserId.value)
}

const fetchRoles = async () => {
  try {
    const response = await request.get('/roles')
    roles.value = response.items || []
  } catch (error) {
    console.error('获取角色列表失败:', error)
  }
}

const showDeleteConfirm = (record: User) => {
  deletingUser.value = record
  deleteVisible.value = true
}

const handleDelete = async () => {
  if (!deletingUser.value) return
  try {
    await request.delete(`/users/${deletingUser.value.id}`)
    message.success('删除成功')
    fetchUsers()
    deleteVisible.value = false
    deletingUser.value = null
  } catch (error) {
    handleError(error, '删除失败，请稍后重试')
  }
}

const handleFormSubmit = async (data: UserFormData) => {
  formLoading.value = true
  try {
    if (editingUserId.value) {
      await request.put(`/users/${editingUserId.value}`, data)
      message.success('更新成功')
    } else {
      await request.post('/users', data)
      message.success('创建成功')
    }
    formVisible.value = false
    fetchUsers()
  } catch (error) {
    handleError(error, editingUserId.value ? '更新失败' : '创建失败')
  } finally {
    formLoading.value = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchRoles()
})
</script>

<style scoped>
.user-list {
  height: 100%;
  overflow: auto;
}

.table-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 300px;
}

.header-right {
  display: flex;
  align-items: center;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .table-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-left,
  .header-right {
    width: 100%;
    justify-content: flex-start;
  }
  
  .header-right {
    margin-top: var(--spacing-sm);
  }
}
</style>
