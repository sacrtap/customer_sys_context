import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import Antd from 'ant-design-vue'
import RoleForm from '../RoleForm.vue'

describe('RoleForm', () => {
  const mockPermissionList = [
    { id: '1', code: 'user:read', name: '查看用户', type: 'api' },
    { id: '2', code: 'user:write', name: '编辑用户', type: 'api' },
    { id: '3', code: 'role:read', name: '查看角色', type: 'api' },
    { id: '4', code: 'role:write', name: '编辑角色', type: 'api' },
    { id: '5', code: 'customer:read', name: '查看客户', type: 'api' },
    { id: '6', code: 'customer:write', name: '编辑客户', type: 'api' }
  ]

  const mockRole = {
    id: '1',
    name: '管理员',
    description: '系统管理员角色',
    is_default: false,
    permissions: [
      { id: '1', code: 'user:read', name: '查看用户', type: 'api' },
      { id: '2', code: 'user:write', name: '编辑用户', type: 'api' }
    ]
  }

  const mountOptions = {
    global: {
      plugins: [Antd]
    }
  }

  it('renders all form fields in create mode', () => {
    const wrapper = mount(RoleForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        permissionList: mockPermissionList
      }
    })
    
    expect(wrapper.find('[data-testid="role-name"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="description"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="is-default"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="permissions"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="submit-btn"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="cancel-btn"]').exists()).toBe(true)
  })

  it('groups permissions by type in tree view', () => {
    const wrapper = mount(RoleForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        permissionList: mockPermissionList
      }
    })
    
    const treeNodes = wrapper.findAll('.ant-tree-treenode')
    // 1 个类型节点 (接口权限) + 6 个权限节点 = 7 个节点
    expect(treeNodes.length).toBe(7)
    expect(treeNodes[0].text()).toContain('接口权限')
  })

  it('prefills form data in edit mode', () => {
    const wrapper = mount(RoleForm, {
      ...mountOptions,
      props: {
        mode: 'edit',
        role: mockRole,
        permissionList: mockPermissionList
      }
    })

    expect(wrapper.find<HTMLInputElement>('[data-testid="role-name"] input').element.value).toBe('管理员')
    expect(wrapper.find<HTMLInputElement>('[data-testid="description"] textarea').element.value).toBe('系统管理员角色')
    expect(wrapper.find<HTMLInputElement>('[data-testid="is-default"] input').element.checked).toBe(false)
  })

  it('validates required fields on submit', async () => {
    const wrapper = mount(RoleForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        permissionList: mockPermissionList
      }
    })
    const submitBtn = wrapper.find('[data-testid="submit-btn"]')

    await submitBtn.trigger('click')
    await vi.waitFor(() => {
      expect(wrapper.find('.ant-form-item-explain').exists()).toBe(true)
    })
  })

  it('selects permissions correctly', async () => {
    const wrapper = mount(RoleForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        permissionList: mockPermissionList
      }
    })
    
    // 选择第一个权限
    const firstCheckbox = wrapper.find('.ant-tree-checkbox')
    await firstCheckbox.trigger('click')
    
    await wrapper.find('[data-testid="submit-btn"]').trigger('click')
    
    await vi.waitFor(() => {
      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')?.[0][0].permission_ids).toContain('1')
    })
  })

  it('emits submit event with form data when validation passes', async () => {
    const wrapper = mount(RoleForm, {
      ...mountOptions,
      props: {
        mode: 'create',
        permissionList: mockPermissionList
      }
    })
    
    await wrapper.find('[data-testid="role-name"] input').setValue('测试角色')
    await wrapper.find('[data-testid="description"] textarea').setValue('测试角色描述')
    // 选择多个权限
    const checkboxes = wrapper.findAll('.ant-tree-checkbox')
    await checkboxes[1].trigger('click') // user:read
    await checkboxes[2].trigger('click') // user:write
    
    await wrapper.find('[data-testid="submit-btn"]').trigger('click')
    
    await vi.waitFor(() => {
      expect(wrapper.emitted('submit')).toBeTruthy()
      expect(wrapper.emitted('submit')?.[0][0]).toEqual(expect.objectContaining({
        name: '测试角色',
        description: '测试角色描述',
        is_default: false,
        permission_ids: ['1', '2']
      }))
    }, { timeout: 2000 })
  })
})
