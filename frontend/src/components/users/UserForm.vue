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
          label="用户名"
          name="username"
          data-testid="username"
        >
          <a-input v-model:value="formData.username" placeholder="请输入用户名" />
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="姓名"
          name="full_name"
          data-testid="full-name"
        >
          <a-input v-model:value="formData.full_name" placeholder="请输入姓名" />
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="邮箱"
          name="email"
          data-testid="email"
        >
          <a-input v-model:value="formData.email" placeholder="请输入邮箱" />
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="电话"
          name="phone"
          data-testid="phone"
        >
          <a-input v-model:value="formData.phone" placeholder="请输入电话号码" />
        </a-form-item>
      </a-col>
      <a-col :span="12" v-if="mode === 'create'">
        <a-form-item
          label="密码"
          name="password"
          data-testid="password"
        >
          <a-input-password v-model:value="formData.password" placeholder="请输入密码" />
        </a-form-item>
      </a-col>
      <a-col :span="12" v-if="mode === 'create'">
        <a-form-item
          label="确认密码"
          name="confirm_password"
          data-testid="confirm-password"
        >
          <a-input-password v-model:value="formData.confirm_password" placeholder="请再次输入密码" />
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="状态"
          name="is_active"
          data-testid="is-active"
        >
          <a-switch v-model:checked="formData.is_active" checked-children="正常" un-checked-children="禁用" />
        </a-form-item>
      </a-col>
      <a-col :span="24">
        <a-form-item
          label="角色"
          name="role_ids"
          data-testid="roles"
        >
          <a-select
            v-model:value="formData.role_ids"
            mode="multiple"
            placeholder="请选择角色"
            style="width: 100%"
          >
            <a-select-option
              v-for="role in roleList"
              :key="role.id"
              :value="role.id"
            >
              {{ role.name }}
            </a-select-option>
          </a-select>
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
import { ref, reactive, watch } from 'vue'
import type { FormInstance } from 'ant-design-vue'

interface Role {
  id: string
  name: string
}

interface UserFormData {
  id?: string
  username: string
  full_name: string
  email: string
  phone: string
  password?: string
  confirm_password?: string
  is_active: boolean
  role_ids: string[]
}

const props = defineProps<{
  mode: 'create' | 'edit'
  user?: UserFormData & { roles?: Role[] }
  roleList: Role[]
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [data: Omit<UserFormData, 'confirm_password'>]
  cancel: []
}>()

const formRef = ref<FormInstance>()
const formData = reactive<UserFormData>({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  password: '',
  confirm_password: '',
  is_active: true,
  role_ids: []
})

const validateConfirmPassword = (_rule: any, value: string) => {
  if (value && value !== formData.password) {
    return Promise.reject(new Error('两次输入的密码不一致'))
  }
  return Promise.resolve()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3到50个字符', trigger: 'blur' }
  ],
  full_name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: props.mode === 'create', message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6到20个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: props.mode === 'create', message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role_ids: [
    { required: true, message: '请至少选择一个角色', trigger: 'change' }
  ]
}

watch(() => props.user, (user) => {
  if (user && props.mode === 'edit') {
    Object.assign(formData, {
      ...user,
      role_ids: user.roles?.map(r => r.id) || []
    })
  }
}, { immediate: true })

const handleSubmit = () => {
  const { confirm_password, ...submitData } = formData
  emit('submit', submitData)
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
