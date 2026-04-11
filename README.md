# AI 智能旅行规划管家 (AI Travel Agent)

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Tech Stack](https://img.shields.io/badge/Tech-Vue3%20%7C%20FastAPI%20%7C%20MySQL%20%7C%20DeepSeek-blue)

这是一个基于大型语言模型（LLM）驱动的全栈智能旅行管家应用。项目融合了 Vue 3 前端、FastAPI 后端以及多智能体（Multi-Agent）技术，能够根据用户需求、预算、游玩节奏，并结合真实的实时天气与交通信息，自动生成高度个性化的每日旅行攻略。

同时系统具备“长短期记忆与画像构建”能力，它会记住用户的旅行偏好，让每次规划都“更懂你”。

## 核心功能特性

- 一键智能行程生成：输入目的地、预算、天数、节奏、兴趣等条件，AI 将规划精确到小时的每日行程、景点安排、预估花费与行前准备。
- AI 用户深度画像记忆：自动提取用户过去的行程习惯（如消费水平、偏好标签、出行人数），对用户进行近期和长期记忆归纳，在后续生成指令中主动运用，生成高度贴合的“专属定制说明”。
- 对话式行程微调：对生成的行程不满意？直接像聊天一样给 AI 发送修改指令（例：“第二天不想去爬山，换个轻松的”），AI 会保留既有上下文进行无缝调整。
- 实时多工具调用 (Tool Integration)：系统底层集成了天气工具、交通计算工具、景点信息工具，在规划前自动抓取并融入决策。
- 行程与数据双轨管载：支持行程的保存、收藏和彻底删除。数据库维持简洁，具体的巨型行程 JSON 自动落盘管理，实现 DB 与物理存储的双轨同步与联动。

## 环境与基本要求

运行该项目，你需要准备以下开发环境：

- Python: 3.8 或以上版本（推荐 3.10+）。
- Node.js: v14+ 以及 npm 进行前端依赖管理。
- MySQL: 运行于本地或远程的 MySQL 8.0 节点。
- 大模型 API Key: 目前接入了 DeepSeek，需要拥有有效的 API Key 余额用于 AI 对话推理。

## 快速开始

### 1. 数据库配置
1. 请确保本地已安装 MySQL，启动服务。
2. 配置数据库账号：默认使用用户名 `Megumi` 及指定密码，您可以到 `backend/database.py` 中修改 `SQLALCHEMY_DATABASE_URL` 为您自己的本地 MySQL 连接字符串。
   ```python
   # 示例 (backend/database.py)
   SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://<您的账号>:<您的密码>@localhost/travel_agent_memory"
   ```
3. 系统会在后端启动时自动建库建表（包含 `users`, `itineraries`, `user_evaluations` 等表）。

### 2. 后端部署 (FastAPI + Python)
1. 进入项目根目录建立虚拟环境并激活：
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
3. 请在代码 (`src/utils/config.py` 或系统环境变量) 中配置正确的 DeepSeek API Key。
4. 启动后端服务 (默认运行在 8000 端口)：
   ```bash
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
   (也可直接运行提供的 `sh run_app.sh` 等脚本启动)

### 3. 前端部署 (Vue 3 + Vite)
1. 打开新终端并进入前端目录：
   ```bash
   cd frontend
   ```
2. 安装 NPM 依赖：
   ```bash
   npm install
   ```
   (也可使用项目自带的 `sh setup_node.sh`)
3. 启动 Vite 开发服务器 (默认代理会自动打通到本地的 8000 后端端口)：
   ```bash
   npm run dev
   ```

## 目录结构概览

```text
travel_agent_project/
├── backend/            # FastAPI 后端路由、数据库配置与模型 (main.py, database.py)
├── frontend/           # Vue 3 前端界面，基于 Vite 构建
│   ├── src/
│   │   ├── components/ # 可复用的基础 Vue 组件
│   │   ├── views/      # 核心页面视图 (首页、规划页、我的行程等)
│   │   └── router/     # 前端路由设置
├── src/                # RAG 和 AI Agent 核心逻辑业务组件
│   ├── agents/         # 智能体层 (PlanningAgent等)
│   ├── tools/          # 对外依赖工具层 (天气、交通距离等接口)
│   ├── services/       # 大模型客户端集成 (DeepSeekClient)
│   └── models.py       # Pydantic 规范的底层数据模型
├── storage/            # 自动生成的本地大文件行程 JSON 存储
├── requirements.txt    # Python 后端依赖清单
└── package.json        # 前端依赖清单
```

## 补充说明

- 安全性过滤：后端带有自动清除 AI 输出Markdown格式符的机制，以确保 JSON 清洁。前端也针对 `localStorage` 中的不同情况做了容错适配。
- 背景评估机制：用户的长短期历史偏好通过 `BackgroundTasks` 异步自动完成，完全不会阻塞页面加载。每次用户的收藏或删除变动也会触发画像更新。


