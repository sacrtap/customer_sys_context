<template>
  <a-modal
    v-model:open="localOpen"
    title="导入客户"
    width="600px"
    :footer="null"
    @cancel="handleCancel"
  >
    <!-- 上传区域 -->
    <div v-if="!importResult" data-testid="upload-area">
      <a-upload-dragger
        :file-list="fileList"
        :before-upload="beforeUpload"
        :show-upload-list="false"
        accept=".xlsx,.xls,.csv"
        :disabled="loading"
      >
        <p class="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p class="ant-upload-text">点击或拖拽文件到此处上传</p>
        <p class="ant-upload-hint">
          支持 Excel (.xlsx, .xls) 和 CSV 文件
        </p>
      </a-upload-dragger>

      <!-- 上传进度 -->
      <div v-if="loading" class="progress-container" data-testid="progress-bar">
        <a-progress :percent="progress" :show-info="false" />
        <p class="progress-text">正在导入，请稍候... {{ progress }}%</p>
      </div>
    </div>

    <!-- 导入结果 -->
    <div v-if="importResult" class="import-result" data-testid="import-result">
      <a-result
        status="success"
        title="导入完成"
        sub-title="共导入 {{ importResult.success + importResult.failed }} 条数据"
      >
        <template #extra>
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="成功">
              <span class="text-success" data-testid="success-count">{{ importResult.success }}</span> 条
            </a-descriptions-item>
            <a-descriptions-item label="失败">
              <span class="text-danger" data-testid="failed-count">{{ importResult.failed }}</span> 条
            </a-descriptions-item>
          </a-descriptions>

          <div v-if="importResult.failed > 0" class="error-list">
            <h4>失败详情：</h4>
            <a-list
              :data-source="importResult.errors"
              :pagination="{ pageSize: 5 }"
            >
              <template #renderItem="{ item }">
                <a-list-item>
                  第 {{ item.row }} 行：{{ item.message }}
                </a-list-item>
              </template>
            </a-list>

            <a-button
              type="primary"
              style="margin-top: 16px"
              data-testid="download-error-btn"
              @click="handleDownloadErrors"
            >
              <DownloadOutlined />
              下载失败记录
            </a-button>
          </div>
        </template>
      </a-result>
    </div>

    <!-- 底部按钮 -->
    <div class="modal-footer">
      <a-space>
        <a-button data-testid="cancel-btn" @click="handleCancel">
          {{ importResult ? '关闭' : '取消' }}
        </a-button>
        <a-button
          type="primary"
          data-testid="upload-btn"
          @click="handleUploadAgain"
          v-if="importResult"
        >
          继续上传
        </a-button>
      </a-space>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { InboxOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import type { UploadFile } from 'ant-design-vue'

interface ImportResult {
  success: number
  failed: number
  errors: Array<{ row: number; message: string }>
}

const props = defineProps<{
  open: boolean
  loading?: boolean
  progress?: number
  importResult?: ImportResult | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'upload': [file: File]
  'download-errors': []
}>()

const localOpen = ref(false)
const fileList = ref<UploadFile[]>([])
const showResult = ref(false)

watch(() => props.open, (value) => {
  localOpen.value = value
  if (!value) {
    fileList.value = []
    showResult.value = false
  }
}, { immediate: true })

watch(() => props.importResult, (result) => {
  if (result) {
    showResult.value = true
  }
}, { immediate: true })

const beforeUpload = (file: UploadFile) => {
  emit('upload', file as unknown as File)
  return false
}

const handleCancel = () => {
  emit('update:open', false)
}

const handleUploadAgain = () => {
  showResult.value = false
  fileList.value = []
}

const handleDownloadErrors = () => {
  emit('download-errors')
}
</script>

<style scoped>
.progress-container {
  margin-top: 24px;
}

.progress-text {
  text-align: center;
  margin-top: 8px;
  color: #666;
}

.import-result {
  padding: 16px 0;
}

.error-list {
  margin-top: 16px;
  text-align: left;
}

.error-list h4 {
  margin-bottom: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.text-success {
  color: #52c41a;
  font-weight: bold;
}

.text-danger {
  color: #ff4d4f;
  font-weight: bold;
}
</style>
