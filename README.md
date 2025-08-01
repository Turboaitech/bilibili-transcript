# Bilibili 视频转文字项目

一个基于 Vercel 部署的 Bilibili 视频转文字服务，使用 Upstash Redis 作为任务队列。

## 项目结构

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
└── README.md              # 说明文档
```

## 功能特性

- 🎥 支持 Bilibili 视频链接提交
- 📝 视频转文字处理
- 🔄 基于 Redis 的任务队列系统
- 🌐 Vercel 无服务器部署
- 🐍 Python 本地轮询处理器
- 📱 响应式前端界面

## 部署步骤

### 1. 准备 Upstash Redis

1. 注册 [Upstash](https://upstash.com/) 账号
2. 创建 Redis 数据库
3. 获取 Redis URL 和 Token

### 2. 部署到 Vercel

#### 方法一：通过 Vercel CLI

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录 Vercel
vercel login

# 部署项目
vercel --prod
```

#### 方法二：通过 GitHub 连接

1. 将代码推送到 GitHub 仓库
2. 在 [Vercel Dashboard](https://vercel.com/dashboard) 导入项目
3. 连接 GitHub 仓库并部署

### 3. 配置环境变量

在 Vercel 项目设置中添加以下环境变量：

```
UPSTASH_REDIS_REST_URL=https://quiet-wahoo-6886.upstash.io
UPSTASH_REDIS_REST_TOKEN=你的token
```

**设置步骤：**
1. 进入 Vercel 项目 Dashboard
2. 点击 Settings 选项卡
3. 点击 Environment Variables
4. 添加上述两个环境变量
5. 重新部署项目

### 4. 本地运行 Python 工作器

```bash
# 安装依赖
pip install requests

# 运行工作器
python worker.py https://your-app.vercel.app

# 或设置环境变量
export API_BASE_URL=https://your-app.vercel.app
python worker.py
```

## 使用方法

### 前端提交任务

1. 访问部署的网站
2. 输入 Bilibili 视频链接
3. 点击提交任务
4. 记录返回的任务ID

### API 接口

#### 提交任务
```http
POST /api/submit-task
Content-Type: application/json

{
  "videoUrl": "https://www.bilibili.com/video/BV1xx411c7mD"
}
```

#### 获取待处理任务
```http
GET /api/get-pending-task
```

#### 更新任务结果
```http
POST /api/get-pending-task
Content-Type: application/json

{
  "taskId": "task_xxx",
  "result": "转录文本内容",
  "error": "错误信息(可选)"
}
```

## 开发说明

### 本地开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Python 工作器说明

`worker.py` 是一个轮询脚本，用于：
- 定期检查 Redis 中的待处理任务
- 下载和处理 Bilibili 视频
- 将转录结果更新回 Redis

**注意**: 当前版本的工作器包含模拟处理逻辑，实际使用时需要集成真实的视频下载和转录服务。

### 扩展功能

可以集成以下服务来实现真实的视频转录：
- [Whisper](https://github.com/openai/whisper) - OpenAI 的语音识别模型
- [讯飞语音](https://www.xfyun.cn/) - 中文语音识别服务
- [YouTube-dl](https://github.com/ytdl-org/youtube-dl) - 视频下载工具

## 注意事项

1. **环境变量安全**: 不要在代码中硬编码 Redis 凭据
2. **任务过期**: Redis 任务设置了 24 小时的过期时间
3. **错误处理**: 工作器包含完整的错误处理和重试机制
4. **资源限制**: 注意 Vercel 和 Upstash 的使用限制

## 故障排除

### 常见问题

1. **API 调用失败**
   - 检查环境变量是否正确设置
   - 验证 Upstash Redis 连接

2. **任务处理失败**
   - 查看工作器日志输出
   - 确认视频链接格式正确

3. **部署问题**
   - 检查 vercel.json 配置
   - 确认所有文件都已提交到 git

## 许可证

MIT License