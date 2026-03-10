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
          label="客户编码"
          name="customer_code"
          data-testid="customer-code"
        >
          <a-input v-model:value="formData.customer_code" placeholder="请输入客户编码" />
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="客户名称"
          name="customer_name"
          data-testid="customer-name"
        >
          <a-input v-model:value="formData.customer_name" placeholder="请输入客户名称" />
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="行业"
          name="industry_id"
          data-testid="industry"
        >
          <a-select v-model:value="formData.industry_id" placeholder="请选择行业">
            <a-select-option value="1">房地产</a-select-option>
            <a-select-option value="2">金融</a-select-option>
            <a-select-option value="3">互联网</a-select-option>
            <a-select-option value="4">制造业</a-select-option>
          </a-select>
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="客户等级"
          name="level_id"
          data-testid="customer-level"
        >
          <a-select v-model:value="formData.level_id" placeholder="请选择客户等级">
            <a-select-option value="1">A级</a-select-option>
            <a-select-option value="2">B级</a-select-option>
            <a-select-option value="3">C级</a-select-option>
            <a-select-option value="4">D级</a-select-option>
          </a-select>
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="联系人"
          name="contact_person"
          data-testid="contact-person"
        >
          <a-input v-model:value="formData.contact_person" placeholder="请输入联系人" />
        </a-form-item>
      </a-col>
      <a-col :span="12">
        <a-form-item
          label="联系电话"
          name="contact_phone"
          data-testid="contact-phone"
        >
          <a-input v-model:value="formData.contact_phone" placeholder="请输入联系电话" />
        </a-form-item>
      </a-col>
      <a-col :span="24">
        <a-form-item
          label="邮箱"
          name="email"
          data-testid="email"
        >
          <a-input v-model:value="formData.email" placeholder="请输入邮箱" />
        </a-form-item>
      </a-col>
      <a-col :span="24">
        <a-form-item
          label="地址"
          name="address"
          data-testid="address"
        >
          <a-textarea v-model:value="formData.address" placeholder="请输入地址" :rows="3" />
        </a-form-item>
      </a-col>
      <a-col :span="24">
        <a-form-item
          label="备注"
          name="remark"
          data-testid="remark"
        >
          <a-textarea v-model:value="formData.remark" placeholder="请输入备注" :rows="3" />
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

interface Customer {
  id?: string
  customer_code: string
  customer_name: string
  industry_id?: string
  level_id?: string
  contact_person?: string
  contact_phone?: string
  email?: string
  address?: string
  remark?: string
  industry?: { id: string; name: string }
  level?: { id: string; name: string }
}

const props = defineProps<{
  mode: 'create' | 'edit'
  customer?: Customer
  loading?: boolean
}>()

const emit = defineEmits<{
  submit: [data: Customer]
  cancel: []
}>()

const formRef = ref<FormInstance>()
const formData = reactive<Customer>({
  customer_code: '',
  customer_name: '',
  industry_id: '',
  level_id: '',
  contact_person: '',
  contact_phone: '',
  email: '',
  address: '',
  remark: ''
})

const rules = {
  customer_code: [
    { required: true, message: '请输入客户编码', trigger: 'blur' }
  ],
  customer_name: [
    { required: true, message: '请输入客户名称', trigger: 'blur' }
  ],
  contact_phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

watch(() => props.customer, (customer) => {
  if (customer && props.mode === 'edit') {
    Object.assign(formData, {
      ...customer,
      industry_id: customer.industry?.id || '',
      level_id: customer.level?.id || ''
    })
  }
}, { immediate: true })

const handleSubmit = () => {
  emit('submit', { ...formData })
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
