<template>
  <div class="role-list page-container">
    <div class="table-card card-container">
      <div class="table-header">
        <div class="header-left">
          <a-typography-title :level="4" style="margin: 0">角色管理</a-typography-title>
        </div>
        <div class="header-right">
          <a-button type="primary" data-testid="add-role-btn" @click="handleAdd">
            <PlusOutlined />
            新建角色
          </a-button>
        </div>
      </div>

      <a-table
        :columns="columns"
        :data-source="roles"
        :loading="loading"
        row-key="id"
        :scroll="{ x: 800 }"
        data-testid="role-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'name'">
            <a-space>
              {{ record.name }}
              <a-tag v-if="record.is_default" color="orange">默认</a-tag>
            </a-space>
          </template>
          <template v-if="column.key === 'permissions'">
            <a-space :size="4">
              <a-tooltip v-for="perm in record.permissions.slice(0, 5)" :key="perm.id" :title="perm.name">
                <a-tag color="green">{{ perm.code }}</a-tag>
              </a-tooltip>
              <a-tag v-if="record.permissions.length > 5" color="default">
                +{{ record.permissions.length - 5 }}
              </a-tag>
            </a-space>
          </template>
           <template v-if="column.key === 'action'">
             <a-space>
               <a data-testid="edit-role-btn" @click="handleEdit(record)">编辑</a>
               <a data-testid="permissions-role-btn" @click="handlePermissions(record)">权限</a>
               <a 
                 v-if="!record.is_default"
                 data-testid="delete-role-btn"
                 class="text-danger" 
                 @click="showDeleteConfirm(record)"
               >
                 删除
               </a>
             </a-space>
           </template>
        </template>
      </a-table>
    </div>

    <a-modal
      v-model:open="formVisible"
      :title="editingRoleId ? '编辑角色' : '新建角色'"
      :footer="null"
      width="600px"
      destroyOnClose
    >
      <RoleForm
        v-if="formVisible && permissions.length > 0"
        :mode="editingRoleId ? 'edit' : 'create'"
        :role="getEditingRole()"
        :permission-list="permissions"
        :loading="formLoading"
        @submit="handleFormSubmit"
        @cancel="formVisible = false"
      />
    </a-modal>

    <a-modal
      v-model:open="permissionVisible"
      title="分配权限"
      :footer="null"
      width="700px"
      destroyOnClose
    >
      <RoleForm
        v-if="permissionVisible && permissions.length > 0"
        :mode="'edit'"
        :role="getEditingRole()"
        :permission-list="permissions"
        :loading="formLoading"
        @submit-permissions="handlePermissionSubmit"
        @cancel="permissionVisible = false"
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
       <p>确定要删除 <strong>{{ deletingRole?.name }}</strong> 吗？</p>
       <a-alert
         type="warning"
         message="此操作不可恢复，请谨慎操作！"
         class="mt-3"
       />
     </a-modal>
    </div>
  </template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import type { ColumnsType } from 'ant-design-vue/es/table'
import { request } from '@/api/request'
import RoleForm from '@/components/roles/RoleForm.vue'

interface Role {
  id: string
  name: string
  description?: string
  is_default: boolean
  permissions: Array<{ id: string; code: string; name: string }>
  created_at: string
}

interface Permission {
  id: string
  code: string
  name: string
  type: string  // api, menu, button
}

interface RoleFormData {
  id?: string
  name: string
  description?: string
  is_default: boolean
  permission_ids: string[]
}

const loading = ref(false)
const roles = ref<Role[]>([])
const permissions = ref<Permission[]>([])
const formVisible = ref(false)
const permissionVisible = ref(false)
const formLoading = ref(false)
const editingRoleId = ref<string | null>(null)
const deleteVisible = ref(false)
const deletingRole = ref<Role | null>(null)

const columns: ColumnsType<Role> = [
  {
    title: '角色名称',
    dataIndex: 'name',
    key: 'name',
    width: 150,
    fixed: 'left',
  },
  {
    title: '描述',
    dataIndex: 'description',
    key: 'description',
    width: 200,
  },
  {
    title: '权限',
    dataIndex: 'permissions',
    key: 'permissions',
    width: 300,
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
    width: 180,
    fixed: 'right',
  },
]

const fetchRoles = async () => {
  loading.value = true
  try {
    const response = await request.get('/roles')
    roles.value = response.data.items || []
  } catch (error) {
    console.error('获取角色列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchPermissions = async () => {
  try {
    const response = await request.get('/roles/permissions')
    permissions.value = response.items || []
  } catch (error) {
    console.error('获取权限列表失败:', error)
  }
}

const getEditingRole = (): RoleFormData & { permissions?: Role['permissions'] } | undefined => {
  if (!editingRoleId.value) return undefined
  const role = roles.value.find(r => r.id === editingRoleId.value)
  if (!role) return undefined
  return {
    ...role,
    permission_ids: role.permissions?.map(p => p.id) || [],
  }
}

const handleAdd = () => {
  editingRoleId.value = null
  formVisible.value = true
}

const handleEdit = (record: Role) => {
  editingRoleId.value = record.id
  formVisible.value = true
}

const handlePermissions = (record: Role) => {
  editingRoleId.value = record.id
  permissionVisible.value = true
}

const showDeleteConfirm = (record: Role) => {
  deletingRole.value = record
  deleteVisible.value = true
}

const handleDelete = async () => {
  if (!deletingRole.value) return
  try {
    await request.delete(`/roles/${deletingRole.value.id}`)
    message.success('删除成功')
    deleteVisible.value = false
    fetchRoles()
  } catch (error) {
    message.error('删除失败，请稍后重试')
    console.error('删除角色失败:', error)
  }
}

const handleFormSubmit = async (data: RoleFormData) => {
  formLoading.value = true
  try {
    if (editingRoleId.value) {
      await request.put(`/roles/${editingRoleId.value}`, data)
      message.success('更新成功')
    } else {
      await request.post('/roles', data)
      message.success('创建成功')
    }
    formVisible.value = false
    fetchRoles()
  } catch (error) {
    message.error(editingRoleId.value ? '更新失败' : '创建失败')
    console.error('表单提交失败:', error)
  } finally {
    formLoading.value = false
  }
}

const handlePermissionSubmit = async (permissionIds: string[]) => {
  formLoading.value = true
  try {
    await request.post(`/roles/${editingRoleId.value}/permissions`, { permission_ids: permissionIds })
    message.success('权限更新成功')
    permissionVisible.value = false
    fetchRoles()
  } catch (error) {
    message.error('权限更新失败')
    console.error('权限更新失败:', error)
  } finally {
    formLoading.value = false
  }
}

onMounted(() => {
  fetchRoles()
  fetchPermissions()
})
</script>

<style scoped>
.role-list {
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
}

.header-left {
  display: flex;
  align-items: center;
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
    gap: var(--spacing-sm);
  }
  
  .header-left,
  .header-right {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
