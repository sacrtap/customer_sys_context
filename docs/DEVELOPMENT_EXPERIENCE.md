# 客户运营中台开发经验总结

**最后更新**: 2026-03-09

---

## 技术选型经验

### 后端框架选择 Sanic

**理由**:
- 异步高性能，适合 I/O 密集型应用
- API 简洁，学习曲线低
- 与 Flask 兼容，易于迁移

**注意事项**:
- Sanic 的 Blueprint 系统适合模块化开发
- 请求对象通过 `request.json` 获取 JSON 数据
- 文件上传通过 `request.files` 获取

### SQLAlchemy 2.0 异步 API

**核心用法**:
```python
# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True)

# Session 工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 查询示例
async with async_session_maker() as session:
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar()
```

**注意事项**:
- 使用 `execute()` + `scalar()` 而不是直接 `get()`
- 事务自动提交，无需手动 commit
- 异常时自动回滚

### JWT 认证实现

**关键代码**:
```python
from jose import jwt

# 生成 Token
to_encode = {
    "sub": str(user.id),
    "username": user.username,
    "exp": datetime.utcnow() + timedelta(minutes=60 * 24 * 7),
}
token = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# 验证 Token
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
user_id = payload.get("sub")
```

**依赖注入**:
```python
async def get_current_user(request) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    token = auth_header.split()[1]
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    # 从数据库获取用户
    return user
```

---

## 前端开发经验

### Vue 3 Composition API

**最佳实践**:
```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const loading = ref(false)

const handleSearch = async () => {
  loading.value = true
  try {
    // API 调用
  } finally {
    loading.value = false
  }
}
</script>
```

### Ant Design Vue 表单验证

```vue
<a-form :model="form" :rules="rules" ref="formRef">
  <a-form-item label="用户名" name="username">
    <a-input v-model:value="form.username" />
  </a-form-item>
</a-form>

<script setup lang="ts">
const form = ref({ username: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
}
</script>
```

### Pinia 状态管理

```typescript
// stores/auth.ts
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))
  
  const login = async (username: string, password: string) => {
    const response = await authApi.login(username, password)
    token.value = response.access_token
    user.value = response.user
    localStorage.setItem('access_token', token.value)
  }
  
  return { user, token, login }
})
```

---

## 数据库设计经验

### PostgreSQL 枚举类型

```python
# 创建枚举
customer_status = postgresql.ENUM(
    'active', 'inactive', 'test',
    name='customerstatus',
    create_type=True
)
customer_status.create(op.get_bind())

# 在模型中使用
status = Column(
    SQLEnum(CustomerStatus),
    default=CustomerStatus.ACTIVE,
    nullable=False,
)
```

### 外键约束

```python
# 级联删除
owner_id = Column(
    UUID(as_uuid=True),
    ForeignKey("users.id", ondelete="SET NULL"),  # 用户删除时设为 NULL
    nullable=True,
)

#  cascade 删除
usages = relationship(
    "CustomerUsage",
    back_populates="customer",
    cascade="all, delete-orphan",  # 客户删除时删除所有用量记录
)
```

---

## 常见问题及解决方案

### 1. CORS 跨域问题

**问题**: 前端无法访问后端 API

**解决**:
```python
# Sanic CORS 配置
from sanic_cors import CORS

CORS(app, origins=[
    "http://localhost:5173",
    "http://localhost:3000",
])
```

### 2. JWT Token 过期处理

**问题**: Token 过期后如何处理

**解决**:
```typescript
// Axios 响应拦截器
service.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      authStore.logout()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)
```

### 3. SQLAlchemy 异步查询

**问题**: 异步查询语法不熟悉

**解决**:
```python
# 单条记录
result = await session.execute(select(User).where(User.id == user_id))
user = result.scalar()

# 多条记录
result = await session.execute(select(User))
users = result.scalars().all()

# 计数
count_result = await session.execute(select(func.count()).select_from(User))
total = count_result.scalar()
```

### 4. Excel 导入中文列名

**问题**: Excel 列名是中文如何映射

**解决**:
```python
FIELD_MAPPING = {
    "客户编码": "customer_code",
    "客户名称": "customer_name",
    "行业": "industry_name",
    "客户等级": "level_code",
}

# 重命名列
df = df.rename(columns=FIELD_MAPPING)
```

---

## 项目结构最佳实践

### 后端目录结构

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/      # 路由定义
│   │       └── __init__.py  # 蓝图注册
│   ├── models/              # SQLAlchemy 模型
│   ├── schemas/             # Pydantic Schema
│   ├── services/            # 业务逻辑
│   ├── utils/               # 工具函数
│   └── database.py          # 数据库配置
├── alembic/                 # 数据库迁移
├── scripts/                 # 运维脚本
├── config.py                # 配置管理
└── main.py                  # 应用入口
```

### 前端目录结构

```
frontend/
├── src/
│   ├── api/                 # API 接口
│   │   ├── request.ts       # Axios 封装
│   │   └── auth.ts          # 认证 API
│   ├── components/          # 公共组件
│   ├── router/              # 路由配置
│   ├── stores/              # Pinia 状态
│   ├── types/               # TypeScript 类型
│   ├── utils/               # 工具函数
│   ├── views/               # 页面视图
│   ├── App.vue              # 根组件
│   └── main.ts              # 入口文件
└── package.json
```

---

## 开发工具推荐

### Python
- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码检查
- **pytest**: 单元测试

### TypeScript/Vue
- **ESLint**: 代码检查
- **Prettier**: 代码格式化
- **Volar**: Vue 3 语言支持

### 数据库
- **DBeaver**: 数据库管理工具
- **pgAdmin**: PostgreSQL 管理

---

## 后续优化方向

1. **性能优化**
   - 数据库查询优化（索引、缓存）
   - 前端组件懒加载
   - API 响应压缩

2. **测试覆盖**
   - 后端单元测试（pytest）
   - 前端组件测试（Vitest）
   - E2E 测试（Playwright）

3. **DevOps**
   - Docker 容器化
   - CI/CD 配置
   - 日志监控

4. **安全加固**
   - SQL 注入防护
   - XSS 防护
   - CSRF 防护

---

*本文档将持续更新，记录开发过程中的经验和教训*
