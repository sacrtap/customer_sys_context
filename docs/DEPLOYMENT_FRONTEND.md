# 前端部署文档

## 概述
本文档描述客户运营中台前端项目的生产环境构建和部署流程。

## 环境要求

- Node.js >= 18.0.0
- NPM >= 9.0.0
- Nginx >= 1.18.0（生产环境）

## 项目配置

### 环境变量配置

项目支持多环境配置，通过 `.env.*` 文件管理：

| 环境 | 配置文件 | 说明 |
|------|----------|------|
| 开发环境 | `.env.development` | 本地开发使用 |
| 测试环境 | `.env.test` | 测试环境部署使用 |
| 生产环境 | `.env.production` | 生产环境部署使用 |

#### 生产环境变量说明

```env
VITE_API_BASE_URL=https://your-domain.com/api/v1  # 后端 API 地址
VITE_APP_TITLE=客户运营中台                        # 应用标题
VITE_APP_VERSION=1.0.0                            # 应用版本号
VITE_ENV=production                               # 环境标识
```

### 构建配置优化

已在 `vite.config.ts` 中实现以下优化：

1. **代码分割**：
   - 将第三方依赖分离为独立 chunk：
     - `vue-vendor`: Vue 生态核心库（vue, vue-router, pinia）
     - `ant-design-vue`: UI 组件库
     - `echarts`: 图表相关库
     - `utils`: 通用工具库（axios, dayjs）
   
2. **资源优化**：
   - 小于 4KB 的静态资源内联为 base64
   - 静态资源按类型分类存放（js/css/images 等）
   - 生产环境自动移除 console 和 debugger 语句
   
3. **压缩优化**：
   - 使用 esbuild 进行代码压缩，构建速度更快
   - 启用 CSS 代码分割，按需加载样式
   - 自动生成 gzip 压缩大小报告

## 部署流程

### 方式一：使用一键部署脚本

项目根目录提供了 `deploy.sh` 脚本，可一键完成构建流程：

```bash
# 进入前端目录
cd frontend

# 给脚本添加执行权限
chmod +x deploy.sh

# 执行部署脚本
./deploy.sh
```

脚本会自动完成以下步骤：
1. 检查 Node.js 版本是否符合要求
2. 安装项目依赖
3. 运行 TypeScript 类型检查
4. 运行 ESLint 代码检查
5. 构建生产版本
6. 检查构建产物并显示大小统计

### 方式二：手动构建

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 类型检查
npm run type-check

# 代码检查
npm run lint

# 构建生产版本
npm run build
```

构建成功后，产物会生成在 `dist` 目录下。

## 生产环境部署

### Nginx 部署

1. **上传构建产物**：将 `dist` 目录上传到服务器指定路径，例如 `/var/www/customer-sys/dist`

2. **配置 Nginx**：参考项目根目录下的 `nginx.conf` 配置文件，根据实际环境修改域名、路径、后端地址等配置。

3. **配置示例**：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       root /var/www/customer-sys/dist;
       index index.html;
       
       # 前端路由支持
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       # 后端 API 代理
       location /api/ {
           proxy_pass http://localhost:8000/;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **重启 Nginx**：
   ```bash
   nginx -t  # 测试配置是否正确
   systemctl restart nginx
   ```

### Docker 部署（可选）

创建 `Dockerfile`：
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

构建并运行：
```bash
docker build -t customer-sys-frontend .
docker run -p 80:80 customer-sys-frontend
```

## 性能指标

### 预期性能
- 首屏加载时间 < 3 秒（4G 网络下）
- 构建后总包体积 < 2MB（gzip 压缩后）
- 静态资源缓存有效期 1 年
- HTML 文件不缓存，保证版本更新及时生效

### 性能优化建议

1. **启用 Gzip/Brotli 压缩**：在 Nginx 中配置 gzip 或 Brotli 压缩，可减少 60% 以上的传输体积
2. **使用 CDN 加速**：将静态资源托管到 CDN，提升全球访问速度
3. **图片优化**：使用 WebP 格式图片，启用图片懒加载
4. **路由懒加载**：路由组件按需加载，减少首屏包体积

## 版本更新流程

1. 拉取最新代码
2. 执行 `./deploy.sh` 脚本构建新版本
3. 备份当前服务器上的 `dist` 目录
4. 将新的 `dist` 目录上传到服务器
5. 验证页面正常加载，功能可用
6. 如有问题，回滚到备份版本

## 常见问题

### 1. 页面刷新出现 404 错误
**原因**：Vue Router 使用 History 模式，Nginx 未配置 fallback 规则
**解决方案**：在 Nginx 配置中添加：
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### 2. 部署后页面没有更新
**原因**：浏览器缓存了旧版本的 HTML 文件
**解决方案**：
- 确保 Nginx 配置中 HTML 文件设置了不缓存
- 强制刷新浏览器（Ctrl+F5）
- 检查构建产物的版本号是否更新

### 3. API 请求报错
**原因**：API 地址配置错误或跨域问题
**解决方案**：
- 检查 `.env.production` 中的 `VITE_API_BASE_URL` 是否正确
- 检查 Nginx 的 API 代理配置是否正确
- 确认后端服务正常运行

### 4. 构建失败
**原因**：依赖缺失或代码存在错误
**解决方案**：
- 删除 `node_modules` 和 `package-lock.json`，重新执行 `npm install`
- 检查 TypeScript 类型错误和 ESLint 错误
- 确保 Node.js 版本符合要求

## 监控与运维

### 访问日志
Nginx 访问日志路径：`/var/log/nginx/access.log`
错误日志路径：`/var/log/nginx/error.log`

### 性能监控
可接入前端监控系统（如 Sentry、ARMS 等）实现：
- 页面加载性能监控
- JavaScript 错误监控
- 用户行为分析
- API 请求成功率监控

## 回滚方案

当部署出现问题时，按以下步骤回滚：
1. 停止服务流量
2. 将备份的旧版本 `dist` 目录恢复
3. 重启 Nginx
4. 验证服务恢复正常
5. 排查问题原因，修复后重新部署

---
**文档版本**：1.0.0
**最后更新**：2026-03-09
