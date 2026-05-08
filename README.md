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

## 1. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
# LLM
API_MODEL=<模型名称>
API_BASE=<OpenAI兼容API地址>
API_KEY=<LLM API Key>

# Redis & PostgreSQL（使用 Docker 内部连接时填以下值）
REDIS_URL=redis://redis:6379/0
POSTGRES_URL=postgresql://agent:agent_password@postgres:5432/agent

# 机器人 ID
AA_ROBOT_ID=<Assistant机器人ID>
GGA_ROBOT_ID=<GreatGroup机器人ID>

# Open API
ORGANIZATION_URL=<机构API地址>
ORGANIZATION_KEY=<机构API Key>
ORG_CODE=<机构代码>

# 服务端口
PORT=5000
```

> `REDIS_URL` 和 `POSTGRES_URL` 使用 Docker 内部服务名（`redis` / `postgres`），不要用 `localhost`。

## 2. 构建并启动

```bash
docker compose up -d --build
```

首次启动会构建镜像并拉取依赖，需要耐心等待。

## 3. 验证服务状态

```bash
# 查看容器状态
docker compose ps

# 健康检查
curl http://localhost:5000/health

# 查看日志
docker compose logs -f app
```

## 4. 更新部署

代码更新后重新构建并启动：

```bash
docker compose up -d --build
```

## 5. 停止服务

```bash
# 停止但保留数据
docker compose down

# 停止并清除数据卷（会丢失所有持久化数据）
docker compose down -v
```
