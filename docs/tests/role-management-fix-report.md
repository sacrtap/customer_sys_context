# 角色管理功能完整修复报告

**修复日期**: 2026-03-10  
**测试脚本**: `frontend/e2e/role-complete-tests.spec.ts`  
**测试框架**: Playwright  

## 测试结果

**总计**: 6/6 通过 (100%) ✅

| 用例编号 | 测试用例 | 状态 | 执行时间 |
|---------|---------|------|---------|
| ① | 角色列表应该正常显示 | ✅ 通过 | ~7.2s |
| ② | 新建角色应该成功 | ✅ 通过 | ~11.1s |
| ③ | 编辑角色应该成功 | ✅ 通过 | ~16.5s |
| ④ | 权限分配应该成功 | ✅ 通过 | ~12.6s |
| ⑤ | 删除角色应该成功 | ✅ 通过 | ~14.1s |
| ⑥ | 默认角色不应该显示删除按钮 | ✅ 通过 | ~6.8s |

**总执行时间**: ~1.2 分钟

## 问题根因

### 1. 后端事务未提交
**文件**: `backend/app/api/v1/routes/roles.py`
- 第 76 行 `create_role` - `flush()` → `commit()`
- 第 128 行 `update_role` - `flush()` → `commit()`
- 第 158 行 `delete_role` - `flush()` → `commit()`
- 第 257 行 `update_role_permissions` - `flush()` → `commit()`

### 2. 前端选择器错误
**文件**: `frontend/src/views/roles/RoleList.vue`
- `data-testid` 位置错误（在 form-item 而非 input 上）
- 删除按钮选择器不匹配

### 3. RoleForm 组件 watch 逻辑不完整
**文件**: `frontend/src/components/roles/RoleForm.vue`
- 未处理 `role` 为空的情况
- 编辑模式下空数据导致表单无法初始化

### 4. 权限对话框条件渲染问题
**文件**: `frontend/src/views/roles/RoleList.vue`
- `v-if="formVisible && permissions.length > 0"` 导致权限列表为空时对话框不渲染

### 5. 权限分配事件命名错误
**文件**: `frontend/src/views/roles/RoleList.vue`
- 使用了不存在的事件 `@submit-permissions`
- 应使用 `@submit` 事件

### 6. RoleList.vue 语法错误
**文件**: `frontend/src/views/roles/RoleList.vue`
- 第 292-294 行有多余代码（之前编辑遗留）
- 导致页面加载失败（500 错误）

### 7. 测试选择器不精确
**文件**: `frontend/e2e/role-complete-tests.spec.ts`
- 使用 `tbody tr` 匹配所有行（包括测量行）
- 应使用 `.ant-table-row` 选择真实数据行

## 修复内容

### 后端修复 (4 处)
```python
# roles.py
# 第 76 行
session.add(role)
await session.commit()  # flush() → commit()

# 第 128 行
await session.commit()  # flush() → commit()

# 第 158 行
await session.commit()  # flush() → commit()

# 第 257 行
await session.commit()  # flush() → commit()
```

### 前端修复 (6 处)

**1. RoleList.vue - 移除 permissions 检查**
```vue
<!-- 编辑对话框 -->
<RoleForm v-if="formVisible" ... />

<!-- 权限对话框 -->
<RoleForm v-if="permissionVisible" ... />
```

**2. RoleList.vue - 权限事件修正**
```vue
<RoleForm @submit="handlePermissionFormSubmit" />
```

**3. RoleList.vue - 添加 handlePermissionFormSubmit 函数**
```typescript
const handlePermissionFormSubmit = async (data: RoleFormData) => {
  formLoading.value = true
  try {
    await request.post(`/roles/${editingRoleId.value}/permissions`, { 
      permission_ids: data.permission_ids 
    })
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
```

**4. RoleList.vue - 删除第 292-294 行多余代码**

**5. RoleForm.vue - watch 逻辑增强**
```typescript
watch(() => props.role, (role) => {
  if (props.mode === 'edit') {
    if (role) {
      Object.assign(formData, {
        ...role,
        permission_ids: role.permissions?.map(p => p.id) || []
      })
    } else {
      // 重置表单
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
```

**6. RoleList.vue - data-testid 位置修正**
```vue
<a-input
  v-model:value="formData.name"
  data-testid="role-name-input"  <!-- 移到 input 上 -->
/>
```

### 测试修复 (2 处)

**1. 测试选择器修正**
```typescript
// 修复前
const rows = page.locator('[data-testid="role-table"] tbody tr')

// 修复后
const rows = page.locator('[data-testid="role-table"] tbody tr.ant-table-row')
```

**2. 删除功能测试优化**
```typescript
// 先创建角色用于删除，然后验证删除成功
// 不依赖消息提示，直接验证数据变化
```

## 关键发现

### 1. Ant Design Vue 表格测量行
使用 `scroll` 属性时，表格会渲染一个 `ant-table-measure-row` 用于虚拟滚动计算。

**解决方案**:
```typescript
// 使用 .ant-table-row 选择真实数据行
const dataRows = page.locator('tbody tr.ant-table-row')
```

### 2. RoleForm 组件事件
RoleForm 组件只 emit `submit` 和 `cancel` 事件，没有 `submit-permissions` 事件。

**解决方案**:
- 统一使用 `@submit` 事件
- 通过 `mode` prop 区分不同模式

### 3. Vue 文件语法错误
语法错误会导致页面完全无法加载，控制台显示 500 错误。

**调试方法**:
```bash
cd frontend
npx vue-tsc --noEmit src/views/roles/RoleList.vue
```

### 4. flush() vs commit()
| 方法 | 作用 | 事务状态 |
|------|------|---------|
| `flush()` | 将更改写入数据库 | 事务未提交，可能回滚 |
| `commit()` | 提交事务 | 更改永久保存 |

**最佳实践**: 在写操作后显式调用 `commit()`

## 运行测试

```bash
cd frontend

# 运行所有测试
npx playwright test e2e/role-complete-tests.spec.ts --project=chromium

# 运行单个测试
npx playwright test e2e/role-complete-tests.spec.ts --grep "①"

# 生成 HTML 报告
npx playwright test e2e/role-complete-tests.spec.ts --reporter=html
npx playwright show-report
```

## 相关文档

- 修复文件:
  - `backend/app/api/v1/routes/roles.py`
  - `frontend/src/views/roles/RoleList.vue`
  - `frontend/src/components/roles/RoleForm.vue`
- 测试脚本: `frontend/e2e/role-complete-tests.spec.ts`
- 经验文档: `AGENTS.md` - "角色管理功能修复 - 增删改查异常"

---

*报告生成时间：2026-03-10*  
*Repository: github.com/sacrtap/customer_sys_context*
