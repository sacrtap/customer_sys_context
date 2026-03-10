# 客户管理功能增强 - TDD 实现报告

**日期**: 2026-03-09  
**任务**: 客户管理功能增强（验证、导入、筛选）  
**开发方式**: TDD（测试驱动开发）

## 实现概述

本次开发使用 TDD 方式增强了客户管理功能，包括：
1. 客户表单验证增强
2. Excel 导入端点（已存在）
3. 客户查询筛选增强

## 测试文件

以下测试文件已存在于 `backend/tests/` 目录：

| 测试文件 | 测试内容 | 测试数量 |
|---------|---------|---------|
| `test_customer_validation.py` | 客户数据验证测试 | 5 个测试 |
| `test_customer_import.py` | Excel 导入测试 | 5 个测试 |
| `test_customer_filters.py` | 客户筛选测试 | 7 个测试 |

## 实现的功能

### 1. 客户验证增强

#### 1.1 手机号格式验证

**文件**: `backend/app/schemas/customer.py`

```python
def validate_phone(value: str | None) -> str | None:
    """验证手机号格式"""
    if value is None:
        return None
    # 中国手机号格式：1 开头，第二位 3-9，后面 9 位数字
    pattern = r'^1[3-9]\d{9}$'
    if value and not re.match(pattern, value):
        raise ValueError('手机号格式不正确')
    return value
```

在 `CustomerBase` 类中添加了 `field_validator`：
```python
_validate_phone = field_validator('contact_phone')(validate_phone)
```

**验证规则**:
- 允许为空
- 必须是 11 位中国手机号格式
- 以 1 开头，第二位是 3-9

#### 1.2 客户编码唯一性验证

**文件**: `backend/app/api/v1/routes/customers.py`

在 `create_customer` 和 `update_customer` 函数中添加了唯一性检查：

```python
# 创建时验证
existing = await session.scalar(
    select(Customer).where(Customer.customer_code == data.customer_code)
)
if existing:
    return json({"error": "客户编码已存在"}, status=400)

# 更新时验证（排除自身）
if data.customer_code and data.customer_code != customer.customer_code:
    existing = await session.scalar(
        select(Customer).where(
            Customer.customer_code == data.customer_code,
            Customer.id != customer_id
        )
    )
    if existing:
        return json({"error": "客户编码已存在"}, status=400)
```

#### 1.3 外键验证

**验证行业 ID**:
```python
if data.industry_id:
    industry = await session.scalar(
        select(Industry).where(Industry.id == data.industry_id)
    )
    if not industry:
        return json({"error": "行业不存在"}, status=400)
```

**验证客户等级 ID**:
```python
if data.level_id:
    level = await session.scalar(
        select(CustomerLevel).where(CustomerLevel.id == data.level_id)
    )
    if not level:
        return json({"error": "客户等级不存在"}, status=400)
```

**验证负责人 ID**:
```python
if data.owner_id:
    owner = await session.scalar(
        select(User).where(User.id == data.owner_id)
    )
    if not owner:
        return json({"error": "负责人不存在"}, status=400)
```

### 2. 客户筛选增强

#### 2.1 按客户等级筛选

**文件**: `backend/app/api/v1/routes/customers.py`

在 `list_customers` 函数中添加了 `level_id` 筛选参数：

```python
# 客户等级筛选
level_id = request.args.get("level_id")
if level_id:
    query = query.where(Customer.level_id == level_id)
```

**支持的筛选参数**:
- `search` - 搜索关键词（客户名称、编码、联系人）
- `status` - 客户状态（active/inactive/test）
- `settlement_status` - 结算状态（settled/unsettled）
- `industry_id` - 行业 ID
- `level_id` - 客户等级 ID（新增）
- `owner_id` - 负责人 ID
- `page` - 页码
- `page_size` - 每页数量

### 3. Excel 导入端点

**文件**: `backend/app/api/v1/routes/customers.py`

导入端点已存在：`POST /api/v1/customers/import`

**功能**:
- 接收 Excel 文件（.xlsx 格式）
- 解析 Excel 数据并验证
- 支持中文列名映射
- 批量导入客户数据
- 返回导入结果（成功/失败记录）

**工具类**: `backend/app/utils/excel_import.py` - `CustomerExcelImporter`

**支持的 Excel 列名**:
| 中文列名 | 字段名 | 必需 |
|---------|-------|------|
| 客户编码 | customer_code | ✓ |
| 客户名称 | customer_name | ✓ |
| 行业 | industry_name | ✗ |
| 客户等级 | level_code | ✗ |
| 状态 | status | ✗ |
| 联系人 | contact_person | ✗ |
| 联系电话 | contact_phone | ✗ |
| 联系邮箱 | contact_email | ✗ |
| 地址 | address | ✗ |
| 结算状态 | settlement_status | ✗ |
| 负责人 | owner_username | ✗ |
| 备注 | remark | ✗ |

## 修改的文件列表

| 文件路径 | 修改内容 |
|---------|---------|
| `backend/app/schemas/customer.py` | 添加手机号验证函数和 field_validator |
| `backend/app/api/v1/routes/customers.py` | 添加唯一性验证、外键验证、等级筛选 |

## 测试用例覆盖

### test_customer_validation.py
- ✅ `test_create_customer_missing_required_fields` - 缺少必填字段
- ✅ `test_create_customer_invalid_email` - 邮箱格式验证（Pydantic EmailStr）
- ✅ `test_create_customer_invalid_phone` - 手机号格式验证（新增）
- ✅ `test_create_customer_invalid_industry` - 行业 ID 验证（新增）
- ✅ `test_create_customer_invalid_level` - 客户等级 ID 验证（新增）
- ✅ `test_create_customer_duplicate_code` - 客户编码重复验证（新增）

### test_customer_import.py
- ✅ `test_import_excel_success` - 成功导入
- ✅ `test_import_excel_partial_failure` - 部分失败
- ✅ `test_import_excel_invalid_format` - 格式错误
- ✅ `test_import_excel_empty_file` - 空文件
- ✅ `test_import_result_format` - 结果格式验证

### test_customer_filters.py
- ✅ `test_filter_by_industry` - 按行业筛选
- ✅ `test_filter_by_level` - 按客户等级筛选（新增）
- ✅ `test_filter_by_status` - 按状态筛选
- ✅ `test_filter_by_settlement_status` - 按结算状态筛选
- ✅ `test_filter_by_owner` - 按负责人筛选
- ✅ `test_filter_combined` - 组合筛选
- ✅ `test_search_by_name` - 搜索功能

## 错误响应格式

### 400 Bad Request
```json
{
    "error": "错误描述"
}
```

**错误类型**:
- `数据验证失败：{详情}` - Pydantic 验证失败
- `客户编码已存在` - 唯一性冲突
- `行业不存在` - 外键验证失败
- `客户等级不存在` - 外键验证失败
- `负责人不存在` - 外键验证失败

### 404 Not Found
```json
{
    "error": "客户不存在"
}
```

## 运行测试

```bash
cd backend
source venv/bin/activate

# 运行所有客户测试
pytest tests/test_customer*.py -v

# 运行验证测试
pytest tests/test_customer_validation.py -v

# 运行导入测试
pytest tests/test_customer_import.py -v

# 运行筛选测试
pytest tests/test_customer_filters.py -v
```

## 后续工作

1. **前端表单集成**
   - 客户创建/编辑表单
   - 实时验证反馈
   - 错误提示展示

2. **Excel 导入 UI**
   - 文件上传组件
   - 导入进度显示
   - 错误结果展示

3. **数据图表**
   - 客户用量趋势图（ECharts）
   - 客户健康度分析
   - 收入预测图表

4. **性能优化**
   - 批量导入优化（分批次处理）
   - 查询索引优化
   - 缓存策略

## 开发经验总结

### 成功经验

1. **Pydantic v2 验证器**: 使用 `field_validator` 装饰器可以轻松添加自定义验证逻辑
2. **SQLAlchemy 2.0**: 异步查询使用 `session.scalar()` 简化单行查询
3. **外键验证时机**: 在业务层（路由）进行外键存在性验证，而不是在数据库层

### 注意事项

1. **手机号验证**: 中国手机号格式为 1[3-9] 开头 + 9 位数字，共 11 位
2. **唯一性检查**: 更新操作需要排除当前记录本身
3. **外键验证**: 需要区分 `None`（不更新）和空字符串（清空关联）

---

*文档生成时间*: 2026-03-09  
*项目*: 客户运营中台系统  
*版本*: v1.0.0
