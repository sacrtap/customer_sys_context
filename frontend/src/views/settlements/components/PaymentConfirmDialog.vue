<template>
  <a-modal
    v-model:open="localOpen"
    title="确认支付"
    width="500px"
    @ok="handleSubmit"
    @cancel="handleCancel"
    :confirm-loading="loading"
  >
    <a-descriptions :column="1" bordered size="small" class="mb-4">
      <a-descriptions-item label="客户名称">{{ settlement?.customer_name }}</a-descriptions-item>
      <a-descriptions-item label="结算月份">{{ settlement?.month }}</a-descriptions-item>
      <a-descriptions-item label="应结金额">¥{{ settlement?.amount.toLocaleString() }}</a-descriptions-item>
    </a-descriptions>

    <a-form
      ref="formRef"
      :model="form"
      layout="vertical"
      @submit.prevent
    >
      <a-form-item
        label="实付金额"
        name="paid_amount"
        :rules="[
          { required: true, message: '请输入实付金额' },
          { type: 'number', min: 0.01, message: '实付金额必须大于0' }
        ]"
      >
        <a-input-number
          v-model:value="form.paid_amount"
          placeholder="请输入实付金额"
          style="width: 100%"
          :min="0.01"
          :precision="2"
          prefix="¥"
        />
      </a-form-item>

      <a-form-item
        label="支付日期"
        name="paid_at"
        :rules="[
          { required: true, message: '请选择支付日期' }
        ]"
      >
        <a-date-picker
          v-model:value="form.paid_at"
          placeholder="请选择支付日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </a-form-item>

      <a-form-item
        label="备注"
        name="remark"
      >
        <a-textarea
          v-model:value="form.remark"
          placeholder="请输入备注"
          :rows="3"
          show-count
          :max-length="200"
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, watch, reactive } from 'vue'
import { message } from 'ant-design-vue'
import type { Settlement, PaymentConfirmRequest } from '@/api/settlement'
import { settlementApi } from '@/api/settlement'

const props = defineProps<{
  open: boolean
  settlement?: Settlement | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'success': []
}>()

const localOpen = ref(props.open)
const formRef = ref()
const loading = ref(false)

const form = reactive<PaymentConfirmRequest>({
  paid_amount: 0,
  paid_at: '',
  remark: ''
})

watch(() => props.open, (val) => {
  localOpen.value = val
  if (val && props.settlement) {
    // 初始化表单
    form.paid_amount = props.settlement.amount
    form.paid_at = new Date().toISOString().split('T')[0]
    form.remark = ''
    formRef.value?.resetFields()
  }
})

watch(() => localOpen.value, (val) => {
  emit('update:open', val)
})

const handleSubmit = async () => {
  if (!props.settlement) return
  
  try {
    await formRef.value?.validate()
    loading.value = true
    
    await settlementApi.confirmPayment(props.settlement.id, {
      paid_amount: form.paid_amount,
      paid_at: form.paid_at,
      remark: form.remark
    })
    
    emit('success')
    localOpen.value = false
  } catch (err: any) {
    message.error('操作失败：' + err.message)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  localOpen.value = false
}
</script>

<style scoped>
.mb-4 {
  margin-bottom: 16px;
}
</style>
