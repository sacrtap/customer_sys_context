import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import Antd from 'ant-design-vue'
import UserForm from '../UserForm.vue'

describe('UserForm', () => {
  const mockRoleList = [
    { id: '1', name: '管理员' },
    { id: '2', name: '普通用户' },
    { id: '3', name: '客户专员' }
  ]

  const mockUser = {
    id: '1',
    username: 'admin',
    full_name: '系统管理员',
    email: 'admin@example.com',
    phone: '13800138000',
    is_active: true,
    roles: [{ id: '1', name: '管理员' }]
  }

  const mountOptions = {
    global: {
      plugins: [Antd]
    }
  }

  it('renders all form fields in create mode', () => {
    const wrapper = mount(UserForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        roleList: mockRoleList
      }
    })
    
    expect(wrapper.find('[data-testid="username"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="full-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="email"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="phone"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="password"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="confirm-password"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="is-active"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="roles"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="submit-btn"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="cancel-btn"]').exists()).toBe(true)
  })

  it('hides password fields in edit mode', () => {
    const wrapper = mount(UserForm, {
      ...mountOptions,
      props: {
        mode: 'edit',
        user: mockUser,
        roleList: mockRoleList
      }
    })
    
    expect(wrapper.find('[data-testid="password"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="confirm-password"]').exists()).toBe(false)
  })

  it('prefills form data in edit mode', () => {
    const wrapper = mount(UserForm, {
      ...mountOptions,
      props: {
        mode: 'edit',
        user: mockUser,
        roleList: mockRoleList
      }
    })

    expect(wrapper.find<HTMLInputElement>('[data-testid="username"] input').element.value).toBe('admin')
    expect(wrapper.find<HTMLInputElement>('[data-testid="full-name"] input').element.value).toBe('系统管理员')
    expect(wrapper.find<HTMLInputElement>('[data-testid="email"] input').element.value).toBe('admin@example.com')
    expect(wrapper.find<HTMLInputElement>('[data-testid="phone"] input').element.value).toBe('13800138000')
    expect(wrapper.find<HTMLInputElement>('[data-testid="is-active"] input').element.checked).toBe(true)
  })

  it('validates required fields on submit', async () => {
    const wrapper = mount(UserForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        roleList: mockRoleList
      }
    })
    const submitBtn = wrapper.find('[data-testid="submit-btn"]')

    await submitBtn.trigger('click')
    await vi.waitFor(() => {
      expect(wrapper.find('.ant-form-item-explain').exists()).toBe(true)
    })
  })

  it('validates password confirmation match', async () => {
    const wrapper = mount(UserForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        roleList: mockRoleList
      }
    })
    
    await wrapper.find('[data-testid="password"] input').setValue('123456')
    await wrapper.find('[data-testid="confirm-password"] input').setValue('1234567')
    await wrapper.find('[data-testid="confirm-password"] input').trigger('blur')
    
    await vi.waitFor(() => {
      expect(wrapper.find('.ant-form-item-explain-error').text()).toContain('两次输入的密码不一致')
    })
  })

  it('emits submit event with form data when validation passes', async () => {
    const wrapper = mount(UserForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        roleList: mockRoleList
      }
    })
    
    await wrapper.find('[data-testid="username"] input').setValue('testuser')
    await wrapper.find('[data-testid="full-name"] input').setValue('测试用户')
    await wrapper.find('[data-testid="email"] input').setValue('test@example.com')
    await wrapper.find('[data-testid="phone"] input').setValue('13900139000')
    await wrapper.find('[data-testid="password"] input').setValue('123456')
    await wrapper.find('[data-testid="confirm-password"] input').setValue('123456')
    // 选择角色
    await wrapper.find('[data-testid="roles"]').trigger('click')
    await vi.waitFor(() => {
      document.querySelector('.ant-select-item[title="管理员"]')?.dispatchEvent(new Event('click'))
    })
    
    await wrapper.find('[data-testid="submit-btn"]').trigger('click')
    
    await vi.waitFor(() => {
      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')?.[0][0]).toEqual(expect.objectContaining({
        username: 'testuser',
        full_name: '测试用户',
        email: 'test@example.com',
        phone: '13900139000',
        password: '123456',
        is_active: true,
        role_ids: ['1']
      }))
    }, { timeout: 2000 })
  })
})
