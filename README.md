# Bilibili 视频转文字项目

一个基于 Vercel 部署的 Bilibili 视频转文字服务，使用 Upstash Redis 作为任务队列。

## 🚀 快速部署

### 1. 部署到 Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/bilibili-transcript)

**手动部署步骤：**
1. Fork 这个仓库到你的 GitHub 账号
2. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
3. 点击 "New Project"
4. 导入你的 GitHub 仓库
5. 配置环境变量（见下方）
6. 点击 "Deploy"

### 2. 配置环境变量

在 Vercel 项目设置中添加以下环境变量：

```
UPSTASH_REDIS_REST_URL=https://quiet-wahoo-6886.upstash.io
UPSTASH_REDIS_REST_TOKEN=ARrmAAIjcDE5Mzc2ZDQxZDRhODE0MzQxYTg4ODQ2YjhlZTIxZDIyZXAxMA
```

**设置步骤：**
1. 进入 Vercel 项目 Dashboard
2. 点击 Settings 选项卡
3. 点击 Environment Variables
4. 添加上述两个环境变量
5. 重新部署项目

## 📁 项目结构

```
bilibili-transcript/
├── api/
│   ├── submit-task.js      # 提交任务 API
│   └── get-pending-task.js # 获取/更新任务 API
├── public/
│   └── index.html          # 前端界面
├── worker.py               # Python 轮询脚本
├── package.json            # 项目依赖
├── vercel.json            # Vercel 配置
├── .env.example           # 环境变量示例
└── README.md              # 说明文档
```

## ✨ 功能特性

- 🎥 支持 Bilibili 视频链接提交
- 📝 视频转文字处理（演示版本）
- 🔄 基于 Redis 的任务队列系统
- 🌐 Vercel 无服务器部署
- 🐍 Python 本地轮询处理器
- 📱 响应式前端界面
- 📊 任务处理统计
- 📝 完整的日志记录

## 🔧 本地开发

### 安装依赖
```bash
npm install
```

### 设置环境变量
```bash
cp .env.example .env.local
# 编辑 .env.local 文件，填入你的 Upstash Redis 信息
```

### 启动开发服务器
```bash
npm run dev
```

### 运行 Python 工作器
```bash
# 安装 Python 依赖
pip install requests

# 运行工作器（替换为你的实际域名）
python worker.py https://your-app.vercel.app
```

## 📚 API 接口

### 提交任务
```http
POST /api/submit-task
Content-Type: application/json

{
  "videoUrl": "https://www.bilibili.com/video/BV1xx411c7mD"
}
```

**响应：**
```json
{
  "success": true,
  "taskId": "task_1234567890_abc123",
  "message": "Task submitted successfully"
}
```

### 获取待处理任务
```http
GET /api/get-pending-task
```

**响应：**
```json
{
  "task": {
    "taskId": "task_1234567890_abc123",
    "videoUrl": "https://www.bilibili.com/video/BV1xx411c7mD",
    "videoId": "BV1xx411c7mD",
    "status": "processing",
    "createdAt": "2024-01-01T00:00:00.000Z"
  }
}
```

### 更新任务结果
```http
POST /api/get-pending-task
Content-Type: application/json

{
  "taskId": "task_1234567890_abc123",
  "result": "转录文本内容...",
  "error": null
}
```

## 🐍 Python 工作器说明

`worker.py` 是一个强大的轮询脚本，具有以下特性：

### 功能特点
- ✅ 自动轮询任务队列
- ✅ 完整的错误处理和重试机制
- ✅ 详细的日志记录
- ✅ 处理统计信息
- ✅ 优雅的退出机制
- ✅ 连接失败保护

### 使用方法
```bash
# 方法 1: 命令行参数
python worker.py https://your-app.vercel.app

# 方法 2: 环境变量
export API_BASE_URL=https://your-app.vercel.app
python worker.py

# 自定义轮询间隔（秒）
export POLL_INTERVAL=10
python worker.py https://your-app.vercel.app
```

### 集成真实转录服务

当前版本包含演示代码。要集成真实的视频转录功能，可以参考以下方案：

#### 方案一：使用 OpenAI Whisper
```bash
pip install yt-dlp whisper ffmpeg-python
```

#### 方案二：使用讯飞语音 API
```bash
pip install websocket-client
```

详细集成代码请参考 `worker.py` 中的注释部分。

## 🔒 安全注意事项

1. **环境变量安全**: 不要在代码中硬编码敏感信息
2. **任务过期**: Redis 任务设置了 24 小时的过期时间
3. **错误处理**: 所有 API 都包含完整的错误处理
4. **CORS 配置**: API 已正确配置跨域访问

## 📊 监控和日志

- Python 工作器会生成 `worker.log` 日志文件
- 包含详细的处理统计信息
- 支持实时状态监控
- 错误信息会同时输出到控制台和日志文件

## 🚨 故障排除

### 常见问题

1. **API 调用失败**
   - 检查环境变量是否正确设置
   - 验证 Upstash Redis 连接
   - 查看 Vercel 函数日志

2. **任务处理失败**
   - 查看 `worker.log` 日志文件
   - 确认视频链接格式正确
   - 检查网络连接

3. **部署问题**
   - 确认 `vercel.json` 配置正确
   - 检查所有必要文件是否提交
   - 验证环境变量设置

### 调试技巧

```bash
# 查看详细日志
tail -f worker.log

# 测试 API 连接
curl https://your-app.vercel.app/api/get-pending-task

# 手动提交测试任务
curl -X POST https://your-app.vercel.app/api/submit-task \
  -H "Content-Type: application/json" \
  -d '{"videoUrl":"https://www.bilibili.com/video/BV1xx411c7mD"}'
```

## 📈 扩展功能建议

- [ ] 添加用户认证系统
- [ ] 实现任务状态查询 API
- [ ] 支持批量视频处理
- [ ] 添加转录结果导出功能
- [ ] 集成更多视频平台支持
- [ ] 实现 WebSocket 实时通知
- [ ] 添加管理后台界面

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**⚡ 快速开始**: 点击上方的 "Deploy with Vercel" 按钮，几分钟内即可拥有自己的视频转文字服务！