<template>
  <a-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    layout="vertical"
    @finish="handleSubmit"
  >
    <a-row :gutter="16">
      <a-col :span="12">
        <a-form-item
          label="角色名称"
          name="name"
        >
          <a-input 
            id="role-name-input" 
            v-model:value="formData.name" 
            placeholder="请输入角色名称" 
            data-testid="role-name-input"
          />
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="是否默认"
          name="is_default"
        >
          <a-switch 
            id="is-default-switch" 
            v-model:checked="formData.is_default" 
            checked-children="是" 
            un-checked-children="否" 
            data-testid="is-default-switch"
          />
        </a-form-item>
      </a-col>
      <a-col :span="24">
        <a-form-item
          label="描述"
          name="description"
        >
          <a-textarea 
            id="description-textarea" 
            v-model:value="formData.description" 
            placeholder="请输入角色描述" 
            :rows="3" 
            data-testid="description-textarea"
          />
        </a-form-item>
      </a-col>
      <a-col :span="24">
        <a-form-item
          label="权限配置"
          name="permission_ids"
        >
          <a-tree
            id="permission-tree"
            v-model:checkedKeys="formData.permission_ids"
            :tree-data="permissionTree"
            checkable
            :default-expand-all="true"
            :field-names="{ title: 'name', key: 'id', children: 'children' }"
            @check="handlePermissionCheck"
            data-testid="permission-tree"
          />
        </a-form-item>
      </a-col>
    </a-row>

    <div class="form-footer">
      <a-space>
        <a-button data-testid="cancel-btn" @click="handleCancel">取消</a-button>
        <a-button type="primary" html-type="submit" data-testid="submit-btn" :loading="loading">
          {{ mode === 'create' ? '新建' : '保存' }}
        </a-button>
      </a-space>
    </div>
  </a-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import type { FormInstance } from 'ant-design-vue'

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

// 导出类型供父组件使用
export type { RoleFormData, Permission }

const props = defineProps<{
  mode: 'create' | 'edit'
  role?: RoleFormData & { permissions?: Permission[] }
  permissionList?: Permission[]
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [data: RoleFormData]
  cancel: []
}>()

const formRef = ref<FormInstance>()
const formData = reactive<RoleFormData>({
  name: '',
  description: '',
  is_default: false,
  permission_ids: []
})

// 构建权限树
const permissionTree = computed(() => {
  // 按类型分组 (api, menu, button)
  const typeMap = new Map<string, any>()
  const typeNames: Record<string, string> = {
    api: '接口权限',
    menu: '菜单权限',
    button: '按钮权限',
  }
  
  // 如果没有权限列表，返回空数组
  if (!props.permissionList || props.permissionList.length === 0) {
    return []
  }
  
  props.permissionList.forEach(perm => {
    const typeName = typeNames[perm.type] || perm.type
    if (!typeMap.has(typeName)) {
      typeMap.set(typeName, {
        id: `type_${perm.type}`,
        name: typeName,
        children: []
      })
    }
    typeMap.get(typeName).children.push({
      id: perm.id,
      name: `${perm.name} (${perm.code})`
    })
  })
  
  return Array.from(typeMap.values())
})

const rules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 20, message: '角色名称长度在2到20个字符', trigger: 'blur' }
  ],
  permission_ids: [
    { required: true, message: '请至少选择一个权限', trigger: 'change' }
  ]
}

watch(() => props.role, (role) => {
  if (props.mode === 'edit') {
    if (role) {
      // 编辑模式且有角色数据
      Object.assign(formData, {
        ...role,
        permission_ids: role.permissions?.map(p => p.id) || []
      })
    } else {
      // 编辑模式但角色数据为空，重置表单
      Object.assign(formData, {
        name: '',
        description: '',
        is_default: false,
        permission_ids: []
      })
    }
  } else {
    // 新建模式，重置表单
    Object.assign(formData, {
      name: '',
      description: '',
      is_default: false,
      permission_ids: []
    })
  }
}, { immediate: true })

const handlePermissionCheck = (checkedKeys: string[]) => {
  formData.permission_ids = checkedKeys.filter(key => !key.startsWith('type_'))
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    emit('submit', { ...formData })
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handleCancel = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  emit('cancel')
}
</script>

<style scoped>
.form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
</style>
