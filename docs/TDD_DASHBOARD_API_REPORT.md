# 数据分析 API 开发实施报告

## 概述

本报告记录了使用 TDD（测试驱动开发）方法开发客户运营中台数据分析 API 的完整过程。

**开发日期**: 2026-03-09  
**技术栈**: Python 3.11+ + Sanic + SQLAlchemy 2.0 + PostgreSQL  
**开发方法**: TDD (Red-Green-Refactor)

---

## 1. 开发内容

### 1.1 新增文件

| 文件路径 | 描述 | 行数 |
|---------|------|------|
| `backend/app/api/v1/routes/dashboard.py` | Dashboard API 路由 | ~450 |
| `backend/app/schemas/dashboard.py` | Dashboard 响应 Schema | ~80 |
| `backend/tests/test_dashboard_api.py` | API 测试文件 | ~550 |
| `backend/scripts/generate_mock_usages.py` | 模拟数据生成脚本 | ~120 |

### 1.2 API 端点

#### 1. 用量趋势 API
```
GET /api/v1/dashboard/usage-trend
```
**参数**:
- `customer_ids` (可选): 客户 ID 列表，逗号分隔
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)

**响应**:
```json
{
  "items": [
    {"date": "2026-01-01", "usageCount": 100, "amount": 1000.00},
    {"date": "2026-02-01", "usageCount": 200, "amount": 2000.00}
  ]
}
```

#### 2. 收入预测 API
```
GET /api/v1/dashboard/revenue-forecast
```
**参数**:
- `months` (可选): 预测月数，默认 3

**响应**:
```json
{
  "items": [
    {"month": "2026-01", "actual": 1000, "forecast": null, "lowerBound": null, "upperBound": null},
    {"month": "2026-04", "actual": null, "forecast": 1500.00, "lowerBound": 1200.00, "upperBound": 1800.00}
  ]
}
```

**算法**: 使用历史数据的移动平均值进行预测，置信区间 = 预测值 ± 1.96 × 标准差

#### 3. 客户分布 API
```
GET /api/v1/dashboard/customer-distribution
```
**参数**:
- `dimension`: 维度 (`industry` | `level`)

**响应**:
```json
{
  "items": [
    {"name": "房地产行业", "value": 50, "percentage": 45.5},
    {"name": "金融行业", "value": 30, "percentage": 27.3}
  ]
}
```

#### 4. 结算状态 API
```
GET /api/v1/dashboard/settlement-status
```
**参数**:
- `year` (可选): 年份，默认当前年

**响应**:
```json
{
  "items": [
    {"month": "2026-01-01", "settled": 5, "unsettled": 2},
    {"month": "2026-02-01", "settled": 8, "unsettled": 1}
  ]
}
```

#### 5. 客户健康度 API
```
GET /api/v1/dashboard/customer-health
```
**响应**:
```json
{
  "summary": {"healthy": 10, "warning": 5, "critical": 2},
  "list": [
    {
      "customer_id": "uuid",
      "customer_name": "客户名称",
      "score": 85.5,
      "level": "healthy",
      "factors": [
        {"name": "用量活跃度", "score": 90, "weight": 0.4},
        {"name": "结算及时性", "score": 80, "weight": 0.3},
        {"name": "用量趋势", "score": 85, "weight": 0.3}
      ]
    }
  ]
}
```

**健康度评分算法**:
1. **用量活跃度 (40%)**: 近 3 个月平均用量 vs 历史平均
2. **结算及时性 (30%)**: 已结算记录比例
3. **用量趋势 (30%)**: 用量增长率

**等级划分**:
- `healthy`: score >= 80
- `warning`: 60 <= score < 80
- `critical`: score < 60

---

## 2. 测试覆盖

### 2.1 测试用例统计

| 测试类 | 测试用例数 | 覆盖内容 |
|--------|-----------|----------|
| TestUsageTrendAPI | 8 | 认证成功/失败、参数验证、空数据、多客户筛选 |
| TestRevenueForecastAPI | 6 | 认证成功/失败、默认值、历史数据不足、置信区间 |
| TestCustomerDistributionAPI | 6 | 按行业/等级分布、认证、百分比总和 |
| TestSettlementStatusAPI | 6 | 认证成功/失败、年度数据、金额计算 |
| TestCustomerHealthAPI | 5 | 认证、健康度评分、等级划分、影响因素 |
| TestDashboardPermissions | 1 | 所有端点权限验证 |
| **总计** | **32** | |

### 2.2 测试类型

- ✅ 认证成功测试 (200 响应)
- ✅ 认证失败测试 (401 响应)
- ✅ 参数验证测试
- ✅ 数据格式验证测试
- ✅ 空数据处理测试
- ✅ 边界条件测试

---

## 3. 技术实现要点

### 3.1 SQLAlchemy 2.0 异步查询

```python
async with request.app.ctx.db() as session:
    query = select(
        extract('year', CustomerUsage.month).label('year'),
        func.sum(CustomerUsage.amount).label('total_amount'),
    ).where(
        CustomerUsage.month >= start_date,
    ).group_by(
        extract('year', CustomerUsage.month),
    )
    
    result = await session.execute(query)
    rows = result.all()
```

### 3.2 日期处理

```python
from datetime import date, timedelta

# 默认最近 3 个月
if not start_date_str:
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
else:
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
```

### 3.3 条件聚合

```python
from sqlalchemy import case

query = select(
    func.sum(
        case(
            (Settlement.status == SettlementStatus.SETTLED, 1),
            else_=0,
        )
    ).label('settled'),
)
```

### 3.4 健康度评分计算

```python
async def calculate_health_score(session, customer: Customer) -> dict:
    factors = []
    score = 0
    
    # 1. 用量活跃度 (40 分)
    activity_score = await calculate_activity_score(session, customer)
    score += activity_score * 0.4
    
    # 2. 结算及时性 (30 分)
    settlement_score = await calculate_settlement_score(session, customer)
    score += settlement_score * 0.3
    
    # 3. 用量趋势 (30 分)
    trend_score = await calculate_trend_score(session, customer)
    score += trend_score * 0.3
    
    # 确定等级
    if score >= 80:
        level = "healthy"
    elif score >= 60:
        level = "warning"
    else:
        level = "critical"
    
    return {"score": score, "level": level, "factors": factors}
```

---

## 4. 遇到的问题及解决方案

### 问题 1: SQLAlchemy 异步驱动配置

**问题**: 使用 `psycopg2` 驱动时出现错误：
```
sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used.
```

**解决方案**: 
1. 安装 `asyncpg` 驱动
2. 更新 `DATABASE_URL` 使用 `postgresql+asyncpg://` 协议

```bash
pip install asyncpg
```

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/customer_sys
```

### 问题 2: 模型缺少 Boolean 导入

**问题**: `role.py` 中使用 `Boolean` 但未导入

**解决方案**: 添加导入
```python
from sqlalchemy import Column, String, ForeignKey, Table, Boolean
```

### 问题 3: 测试 Fixture 依赖

**问题**: 测试需要 `mixed_customers` fixture 但 conftest 中未定义

**解决方案**: 在 `conftest.py` 中添加 fixture
```python
@pytest_asyncio.fixture
async def mixed_customers(sample_industry, sample_customer_level):
    """创建多个测试客户用于统计测试"""
    async with database.session() as session:
        customers = []
        for i in range(3):
            customer = Customer(...)
            session.add(customer)
            customers.append(customer)
        await session.flush()
        yield customers
```

---

## 5. 代码质量

### 5.1 代码规范

- ✅ 遵循 PEP 8 规范
- ✅ 使用类型注解
- ✅ 函数添加 docstring
- ✅ 使用 Black 格式化

### 5.2 错误处理

```python
try:
    year = int(year_str) if year_str else datetime.now().year
except ValueError:
    year = datetime.now().year
```

### 5.3 性能优化

- 使用异步数据库查询
- 批量数据处理
- 适当的数据库索引

---

## 6. 下一步计划

### 6.1 待完成功能

1. **前端图表展示**
   - ECharts 集成
   - 用量趋势图
   - 客户分布饼图
   - 健康度仪表

2. **数据导出**
   - Excel 导出功能
   - PDF 报告生成

3. **性能优化**
   - 查询结果缓存 (Redis)
   - 预计算汇总数据

### 6.2 测试完善

- [ ] 运行完整测试套件验证
- [ ] 添加性能测试
- [ ] 添加集成测试

---

## 7. 总结

本次开发遵循 TDD 方法，先编写测试用例（Red 阶段），然后实现最简代码让测试通过（Green 阶段），最后进行重构优化（Refactor 阶段）。

**主要成果**:
1. ✅ 完成 5 个 Dashboard API 端点
2. ✅ 实现收入预测算法
3. ✅ 实现客户健康度评分系统
4. ✅ 编写 32 个测试用例
5. ✅ 创建模拟数据生成脚本

**代码统计**:
- 新增代码：~1200 行
- 测试代码：~550 行
- 测试覆盖率：待运行统计

---

*最后更新：2026-03-09*  
*Repository: github.com/sacrtap/customer_sys_context*
