# OpenList Episode Rename

一个基于 Web UI 的 OpenList 剧集批量重命名工具，支持 TMDB 剧集信息自动抓取、命名规则自定义（配置页管理 TMDB API Key / 分隔符等）、深色/浅色主题切换、目录重命名等。

# 预览图

![Web UI 预览](image/demo01.webp)
![Web UI 预览](image/demo02.webp)

## 项目结构

```
openlist_episode_rename/
├── core.py              # 核心逻辑（OpenList API 封装、剧集识别、重命名引擎、配置持久化）
├── server.py            # FastAPI Web 服务端
├── frontend/
│   └── index.html       # Vue 3 + Element Plus 前端页面
├── .github/workflows/   # CI/CD 自动发布
├── .gitignore
├── LICENSE
└── README.md
```

## 功能特性

- **现代化 Web 界面** — 干净的设计系统，支持深色/浅色主题一键切换
- **目录浏览与重命名** — 侧边栏树形导航，点击目录进入，支持直接重命名目录
- **智能重命名预览** — 进入目录自动识别剧集文件并生成新文件名预览，勾选后一键批量执行
- **命名规则自定义** — 配置页管理：分隔符（点/下划线/空格/短横线）、是否包含集标题、默认季/集
- **TMDB 集成** — 配置页管理 TMDB API Key：有 Key 走官方 API（更快更稳），无 Key 自动回退网页抓取
- **批量重命名** — 一键递增季(S)/集(E)编号，批量附加标签，字幕文件自动跟随同集视频
- **登录持久化** — 登录信息保存到 localStorage，刷新不丢失

## 快速开始

### 安装依赖

```bash
pip install requests fastapi uvicorn beautifulsoup4
```

### 启动 Web 服务

```bash
python server.py
```

浏览器打开 `http://127.0.0.1:8000`，输入 OpenList 服务地址、用户名和密码即可登录使用。

## 使用说明

1. **登录** — 在 Web UI 输入 OpenList 服务地址和账号密码
2. **导航** — 侧边栏点击目录进入，面包屑导航快速跳转
3. **重命名** — 进入目录后自动生成新文件名预览，勾选文件点击"批量重命名"执行；也可用 TMDB 自动补全剧名/集标题或手动编辑
4. **目录重命名** — 侧边栏点击目录行的重命名图标
5. **配置** — 顶栏 ⚙ 按钮打开配置页：TMDB API Key、命名规则、主题等
6. **主题切换** — 顶栏 🌙/☀️ 按钮切换深色/浅色模式

## 依赖

| 依赖                 | 用途              |
| -------------------- | ----------------- |
| FastAPI + Uvicorn    | Web 服务框架      |
| Vue 3 + Element Plus | 前端 UI           |
| BeautifulSoup4       | TMDB 网页回退解析 |
| requests             | HTTP 请求         |

## 许可证

MIT License
