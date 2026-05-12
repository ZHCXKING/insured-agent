# AssistantAgent - Docker 部署指南

## 架构概览

项目包含三个服务：

| 服务 | 说明 | 端口 |
|---|---|---|
| **app** | Flask 应用（AssistantAgent + GreatGroupAgent） | 5000 |
| **redis** | Redis Stack（会话缓存 + 检查点存储） | 6379 |
| **postgres** | PostgreSQL（长期记忆存储） | 5432 |

## 前置要求

- Docker >= 24
- Docker Compose >= v2
- Git

## 1. 克隆项目

```bash
git clone <仓库地址>
```

## 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# ===== LLM 配置 =====
API_MODEL=<模型名称，如 gpt-4o>
API_BASE=<OpenAI 兼容 API 地址，如 https://api.openai.com/v1>
API_KEY=<LLM API Key>

# ===== 数据库（Docker 内部连接使用服务名，不要用 localhost）=====
REDIS_URL=redis://redis:6379/0
POSTGRES_URL=postgresql://agent:agent_password@postgres:5432/agent

# ===== WorkTool机器人ID =====
AA_ROBOT_ID=<Assistant 机器人 ID>
GGA_ROBOT_ID=<GreatGroup 机器人 ID>

# ===== 机构 Open API =====
ORGANIZATION_URL=<机构 API 地址>
ORGANIZATION_KEY=<机构 API Key>
ORG_CODE=<机构代码>

# ===== 服务端口 =====
PORT=5000

# ===== ngrok（可选，外网暴露时需要）=====
# NGROK_AUTHTOKEN=<ngrok authtoken>
```

> **重要**：`REDIS_URL` 和 `POSTGRES_URL` 使用 Docker 内部服务名（`redis` / `postgres`），不要用 `localhost`。

## 3. 构建并启动

```bash
docker compose up -d --build
```

首次启动会构建镜像并拉取依赖，需要耐心等待。

## 4. 验证服务状态

```bash
# 查看容器状态
docker compose ps

# 健康检查
curl http://localhost:5000/health

# 查看日志
docker compose logs -f app
```

## 5. 更新部署

代码更新后重新构建并启动：

```bash
git pull
docker compose up -d --build
```

## 6. 停止服务

```bash
# 停止但保留数据
docker compose down

# 停止并清除数据卷（会丢失所有持久化数据）
docker compose down -v
```

## 7. 外网暴露（可选）

如需将本地服务暴露到公网（如对接企微回调），可使用 ngrok：

```bash
# 先在 .env 中配置 NGROK_AUTHTOKEN
pip install -r requirements.txt
python ngrok_launcher.py
```
