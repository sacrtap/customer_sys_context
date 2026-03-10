import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import Antd from 'ant-design-vue'
import ImportDialog from '../ImportDialog.vue'

describe('ImportDialog', () => {
  const mountOptions = {
    global: {
      plugins: [Antd]
    }
  }

  it('renders upload area when visible', () => {
    const wrapper = mount(ImportDialog, {
      ...mountOptions,
      props: {
        open: true
      }
    })

    expect(wrapper.find('[data-testid="upload-area"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="upload-btn"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="cancel-btn"]').exists()).toBe(true)
  })

  it('emits update:open event when cancel is clicked', async () => {
    const wrapper = mount(ImportDialog, {
      ...mountOptions,
      props: {
        open: true
      }
    })

    await wrapper.find('[data-testid="cancel-btn"]').trigger('click')
    expect(wrapper.emitted('update:open')?.[0][0]).toBe(false)
  })

  it('shows progress bar during upload', async () => {
    const wrapper = mount(ImportDialog, {
      ...mountOptions,
      props: {
        open: true,
        loading: true,
        progress: 50
      }
    })

    expect(wrapper.find('[data-testid="progress-bar"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="progress-bar"]').attributes('percent')).toBe('50')
  })

  it('shows import result after upload', () => {
    const wrapper = mount(ImportDialog, {
      ...mountOptions,
      props: {
        open: true,
        importResult: {
          success: 10,
          failed: 2,
          errors: [
            { row: 2, message: '客户编码重复' },
            { row: 5, message: '手机号格式错误' }
          ]
        }
      }
    })

    expect(wrapper.find('[data-testid="import-result"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="success-count"]').text()).toContain('10')
    expect(wrapper.find('[data-testid="failed-count"]').text()).toContain('2')
    expect(wrapper.find('[data-testid="download-error-btn"]').exists()).toBe(true)
  })

  it('emits upload event when file is selected', async () => {
    const wrapper = mount(ImportDialog, {
      ...mountOptions,
      props: {
        open: true
      }
    })

    const file = new File(['test content'], 'customers.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const uploadInput = wrapper.find('input[type="file"]')
    await uploadInput.setValue(file)

    await vi.waitFor(() => {
      expect(wrapper.emitted('upload')).toBeTruthy()
      expect(wrapper.emitted('upload')?.[0][0]).toBe(file)
    })
  })

  it('emits download-errors event when download button is clicked', async () => {
    const wrapper = mount(ImportDialog, {
      ...mountOptions,
      props: {
        open: true,
        importResult: {
          success: 10,
          failed: 2,
          errors: []
        }
      }
    })

    await wrapper.find('[data-testid="download-error-btn"]').trigger('click')
    expect(wrapper.emitted('download-errors')).toBeTruthy()
  })
})
