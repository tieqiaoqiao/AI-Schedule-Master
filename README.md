# 🎓 超级大学生日程管家 (AI Schedule Master)

> 一款基于大语言模型（LLM）与多格式文件解析的智能时间管理助手。告别繁琐的死记硬背，直接把课表、排班表扔给 AI，一句话帮你查出时间冲突！

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![LangChain](https://img.shields.io/badge/LangChain-Framework-yellow.svg)

---

## ✨ 核心功能 (Features)

- 📂 **多格式文件解析**：支持同时上传多个 `.txt` 或 `.csv` 格式的课表与部门排班表，前端利用 `FileReader` 异步读取，无缝拼接给大模型。
- 🧠 **大模型原生推理**：抛弃传统的 `if-else` 时间比对，直接利用 DeepSeek 强大的长上下文语义理解能力，跨文本进行时间冲突排查。
- ⚡ **流式打字机输出**：基于 FastAPI 的 `StreamingResponse` 与前端 `ReadableStream`，实现文字逐字吐出，彻底告别等待焦虑。
- 💾 **企业级数据持久化**：底层重构为 **MySQL** 数据库，利用 `PyMySQL` 与 `DictCursor` 实现聊天记录的隔离与高效存储。
- 🛡️ **高健壮性**：前后端全面捕获异常，针对大模型换行符断流、数据库连接超时等边缘场景做了完善的防坑处理。

## 🛠️ 技术栈 (Tech Stack)

- **前端**：HTML5, CSS3, Vanilla JavaScript (Fetch API, FileReader, ReadableStream)
- **后端**：Python 3.10, FastAPI, Uvicorn, Pydantic
- **AI 驱动**：LangChain, DeepSeek API
- **数据库**：MySQL, PyMySQL

---

## 🚀 快速开始 (Quick Start)

### 1. 环境准备
确保你的电脑上安装了 Python 3.10+ 和 MySQL 8.0+。

### 2. 安装依赖
```bash
pip install fastapi uvicorn pymysql pydantic langchain langchain-deepseek
```

### 3. 配置环境变量
在项目根目录下新建一个 `.env` 文件，填入你的 API Key 和数据库配置：
```env
DEEPSEEK_API_KEY=你的DeepSeek密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

*(注意：请在 `database.py` 中配置你本地的 MySQL 账号和密码)*

### 4. 启动后端服务
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. 运行前端
直接在浏览器中双击打开 `index.html` 即可使用。上传你的课表文件，开始提问吧！

---

## 📸 界面展示 (Screenshots)

![pnDnXjI.png](https://s41.ax1x.com/2026/10/23/pnDnXjI.png)


---

## 📝 开发心得 (Learnings)

作为大二学生的全栈实战项目，本项目在开发过程中攻克了以下技术难点：
1. **SSE (Server-Sent Events) 流式传输**：解决了大模型生成长文本时的 HTTP 超时与阻塞问题。
2. **JSON 安全包装**：解决了流式传输中，大模型输出带有 `\n` 换行符导致前端 `split('\n\n')` 解析错乱的 Bug。
3. **异步数据库落盘**：引入 `BackgroundTasks`，确保在流式输出结束后，数据库写入不会卡住网络连接。

## 📄 开源协议 (License)

本项目采用 [MIT License](LICENSE) 协议开源。
