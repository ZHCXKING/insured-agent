# AssistantAgent - Docker 部署指南

## 架构概览

项目包含三个 AI 代理，通过微信群聊接收消息并处理：

| 代理 | 目录 | 触发规则 | 功能 |
|---|---|---|---|
| **AssistantAgent** | `AssistantAgent/` | 默认（其他群） | 预约/客户/保单业务 CRUD |
| **GreatGroupAgent** | `GreatGroupAgent/` | 群名包含 "support"（不区分大小写） | 创建群聊 |
| **LicenseAssistantAgent** | `LicenseAssistant/` | 群名包含 "预备" | 保险考试知识检索 |

Docker Compose 包含三个服务：

| 服务 | 说明 | 端口 |
|---|---|---|
| **app** | Flask 应用（gunicorn, 1 worker, 300s 超时） | 5000 |
| **redis** | Redis Stack（会话缓存 + 检查点 + 分布式锁 + 定时任务） | 6379 |
| **postgres** | PostgreSQL（长期记忆存储） | 5432 |

## 前置要求

- Docker >= 24
- Docker Compose >= v2
- Git

## 1. 克隆项目

```bash
git clone <仓库地址>
cd AssistantAgent
```

## 2. 配置环境变量

在项目根目录创建 `.env` 文件（此文件已被 `.gitignore` 忽略，不会提交到仓库）：

```env
# ===== LLM 配置 =====
API_MODEL=<模型名称，如 gpt-4o>
API_BASE=<OpenAI 兼容 API 地址，如 https://api.openai.com/v1>
API_KEY=<LLM API Key>

# ===== 数据库（Docker 内部连接使用服务名，不要用 localhost）=====
REDIS_URL=redis://redis:6379/0
POSTGRES_URL=postgresql://agent:agent_password@postgres:5432/agent

# ===== WorkTool 机器人 ID =====
AA_ROBOT_ID=<Assistant 机器人 ID>
GGA_ROBOT_ID=<GreatGroup 机器人 ID>
LA_ROBOT_ID=<LicenseAssistant 机器人 ID>

# ===== 机构 Open API =====
ORGANIZATION_URL=<机构 API 地址>
ORGANIZATION_KEY=<机构 API Key>
ORG_CODE=<机构代码>

# ===== 服务端口 =====
PORT=5000
```

> **重要**：`REDIS_URL` 和 `POSTGRES_URL` 使用 Docker 内部服务名（`redis` / `postgres`），不要用 `localhost`。

可选配置：

```env
# ===== LicenseAssistant RAG（不配置则回退到 API_BASE/API_KEY）=====
EMBEDDING_API_BASE=<Embedding API 地址>
EMBEDDING_API_KEY=<Embedding API Key>
EMBEDDING_MODEL=<Embedding 模型名称>

# ===== ngrok 外网暴露 =====
NGROK_AUTHTOKEN=<ngrok authtoken>
```

## 3. 构建并启动

```bash
docker compose up -d --build
```

首次启动会构建镜像（基于 Python 3.14-slim）并拉取依赖，需要耐心等待。

`app` 服务依赖 `redis` 和 `postgres` 健康检查通过后才会启动，无需手动控制启动顺序。

## 4. 验证服务状态

```bash
# 查看容器状态（三个服务均应为 healthy）
docker compose ps

# 健康检查
curl http://localhost:5000/health

# 查看应用日志
docker compose logs -f app

# 查看所有服务日志
docker compose logs -f
```

健康检查返回 `{"status": "ok"}` 即表示服务正常运行。

## 5. 更新部署

代码更新后重新构建并启动：

```bash
git pull
docker compose up -d --build
```

仅重启 app 服务（不重建镜像）：

```bash
docker compose restart app
```

## 6. 停止服务

```bash
# 停止但保留数据（Redis + PostgreSQL 数据卷保留）
docker compose down

# 停止并清除数据卷（会丢失所有持久化数据，包括 ChromaDB 向量库）
docker compose down -v
```

## 7. 外网暴露（可选）

如需将本地服务暴露到公网（如对接企微回调），可使用 ngrok：

```bash
# 先在 .env 中配置 NGROK_AUTHTOKEN
pip install -r requirements.txt
python ngrok_launcher.py
```

启动后会输出公网地址，将 `{公网地址}/message` 配置为企微回调 URL 即可。

## API 端点

| 端点 | 方法 | 说明 |
|---|---|---|
| `/message` | POST | 接收微信群聊消息，根据群名路由到对应代理 |
| `/QRcode` | POST | 接收群二维码回传（GreatGroupAgent 创建群流程） |
| `/health` | GET | 健康检查 |
