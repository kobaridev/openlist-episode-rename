# OpenList Episode Rename

基于 Web UI 的 OpenList 剧集批量重命名工具。支持目录浏览与目录重命名、剧集名自动识别、TMDB 集名抓取（官方 API / 网页抓取双通道）、季(S)/集(E)批量编号、媒体参数批量附加、字幕文件自动跟随同集视频，以及深色/浅色主题切换。

# 预览图

![Web UI 预览](image/demo01.webp)

![TMDB 剧集抓取预览](image/demo02.webp)

## 项目结构

```
openlist-episode-rename/
├── core.py                      # 核心逻辑（OpenList API 封装、剧集识别、重命名引擎、配置持久化）
├── server.py                    # FastAPI Web 服务端（托管前端 + REST API）
├── frontend/
│   └── index.html               # Vue 3 + Element Plus 前端页面（单文件）
├── .github/workflows/Release.yml# 主分支推送自动打标签并发布 Release
├── Dockerfile                  # 生产部署镜像（FastAPI 服务 + 前端资源）
├── Dockerfile.dev              # 开发容器（python:3.12-slim + 项目依赖）
├── docker-compose.yml          # Docker 一键部署编排
├── requirements.txt            # Python 依赖清单
├── .devcontainer/              # VS Code Dev Container 配置
├── openlist-episode-renamer.spec# PyInstaller 打包配置
├── image/                       # README 预览图
├── USERPROFILE/                 # 本地配置/令牌示例（episode_renamer.conf、token）
├── .gitignore
├── LICENSE
└── README.md
```

## 功能特性

- **现代化 Web 界面** — 干净的设计系统，顶栏 🌙/☀️ 一键切换深色/浅色主题
- **目录浏览与重命名** — 侧边栏树形导航，面包屑路径快速跳转，支持直接重命名目录
- **剧集自动识别** — 进入目录自动识别媒体文件与字幕文件并生成新文件名预览（✓/? 标记有效性）
- **TMDB 集成** — 按剧名搜索，选中即拉取对应季的集名自动回填；设置页配置 TMDB API Key 后走官方 API（更稳定），留空自动回退到网页抓取
- **批量编号** — 「季」「起始集号」数字框 + 「应用」一键为列表递增 S/E 编号
- **媒体参数** — 输入框内输入参数后按回车生成标签块（如 `1080p`），可继续追加多个，一键应用到 参数 列（回车分隔输入，✕ 删除单个）
- **字幕跟随** — 同名 `.srt/.ass` 等字幕文件与对应视频文件保持同一新文件名
- **自定义设置** — 设置抽屉管理 TMDB API Key、文件名分隔符（点/下划线/空格/短横线），其余选项直接在工具栏提供；登录与设置自动持久化

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动 Web 服务

```bash
python server.py
```

浏览器打开 `http://127.0.0.1:8000`，输入 OpenList 服务地址、用户名和密码即可登录使用。

可选监听地址：`python server.py 0.0.0.0 8000`（默认 `127.0.0.1:8000`）。

## 直接下载运行（编译产物）

无需 Python 环境，直接从仓库的 [Releases](../../../releases) 下载对应平台产物即可使用：
启动后服务监听 `0.0.0.0:8000`，浏览器打开 `http://127.0.0.1:8000`，登录你的 OpenList 服务地址（默认端口 5244）即可。配置/令牌保存在 `$EPISODE_PATH`（默认 `/tmp`，Linux deb 服务为 `/var/lib/openlist-episode-rename`）。

> 平台产物均为按架构编译：Windows/Linux 分 **amd64(x64)** 与 **arm64**，macOS 分 **x64** 与 **arm64**，请按设备架构选择。

### Windows

```powershell
.\openlist-episode-renamer-windows-amd64.exe
# 浏览器打开 http://127.0.0.1:8000；关闭该终端即停止服务
```

### Linux

**AppImage（免安装运行）**

```bash
chmod +x openlist-episode-renamer-linux-x86_64.AppImage     # arm64 机型用 -aarch64.AppImage
./openlist-episode-renamer-linux-x86_64.AppImage
# 无 FUSE 环境时用: ./openlist-episode-renamer-linux-x86_64.AppImage --appimage-extract-and-run
```

**deb 包（可注册为系统服务）**

```bash
sudo dpkg -i openlist-episode-renamer_<版本>_amd64.deb      # arm64 用对应 _arm64.deb
sudo apt-get install -f                                      # 如有未满足依赖
sudo systemctl enable --now openlist-episode-renamer         # 开机自启并启动
# 日志: journalctl -u openlist-episode-renamer -f
```

### macOS（DMG）

```bash
hdiutil attach openlist-episode-renamer-macos-arm64.dmg     # Intel 用 -x64.dmg
# 将 openlist-episode-renamer 拷出后运行：
./openlist-episode-renamer
# 首次被 Gatekeeper 拦截：右键 → 打开；或:
#   xattr -d com.apple.quarantine ./openlist-episode-renamer
```

## Docker 部署

项目自带多阶段生产镜像 `Dockerfile` 与编排文件：

```bash
# 构建并启动（后台运行，容器名 openlist-episode-rename）
docker compose up -d --build

# 查看日志 / 停止
docker compose logs -f
docker compose down
```

- 浏览器访问 `http://127.0.0.1:8000`；
- 设置与登录令牌通过命名卷 `ep-data` 持久化（容器内 `/data`）；
- 容器默认使用网络桥接，登录页的 OpenList 地址若在宿主机上，请填 `http://host.docker.internal:5244`（默认端口 5244）。

> 若宿主机 8000 端口被占用（例如本机已在跑 8000 的 Web 服务），可改 `docker-compose.yml` 的端口映射，如 `"8001:8000"`；
> 若与 OpenList 同机同网段且走 host 网络更顺，可把 compose 中的映射改回 `network_mode: host`（此时服务直绑宿主机 8000）。

### 依赖层「openlist-episode-rename:base」复用（离线构建）

pip 首次下载依赖卡在 `pip install 4/6`？`Dockerfile` 分两阶段，把「装好依赖」做成独立镜像层，构建一次永久复用，之后改代码只 COPY 本地文件、完全离线秒级完成：

```bash
# 1. 构建依赖层（默认走清华镜像源，约 30 秒；也可换阿里云或官方源）
docker build --target deps -t openlist-episode-rename:base .
#    docker build --target deps --build-arg PIP_INDEX=https://mirrors.aliyun.com/pypi/simple -t openlist-episode-rename:base .
#    docker build --target deps --build-arg PIP_INDEX=https://pypi.org/simple  -t openlist-episode-rename:base .

# 2. 之后任何一次应用构建都在 base 上直接 COPY 仓库文件，不再联网
docker build -t openlist-episode-rename:latest .
```

### 开发容器

```bash
docker build -f Dockerfile.dev -t openlist-episode-rename:dev .
docker run -it --rm --network host -v "$(pwd):/work" -w /work openlist-episode-rename:dev bash
```

VS Code 可直接打开仓库的 `.devcontainer/` 配置进入开发容器（`--network host`，容器内直连宿主机 OpenList 并绑定 `127.0.0.1:8000`）。

## 使用说明

1. **登录** — Web UI 输入 OpenList 服务地址和账号密码，连接成功即进入目录
2. **导航** — 侧边栏点击目录进入，顶栏面包屑显示当前路径，⬆ 上一级 快速返回
3. **识别与预览** — 进入目录后文件列表自动生成新文件名预览，可手动编辑 Season / Episode / 集名 / 参数
4. **批量编号** — 在工具栏设置「季」「起始集号」，点击「应用」为列表批量递增编号
5. **TMDB 抓取** — 「🔍 搜索」剧名 → 选中剧集卡片 → 「⚡ 获取集名」自动回填集名列；集名可在每行编辑或留空
6. **媒体参数** — 在参数输入框输入如 `1080p` 后按回车添加，可继续添加多个，点「应用参数」批量填入参数列；参数为空时点「应用参数」会清空该列
7. **确认重命名** — 底部点击「⚡ 确认重命名 N 个文件」批量执行；目录重命名使用独立面板
8. **设置** — 顶栏 ⚙ 打开设置抽屉：TMDB API Key、文件名分隔符
9. **主题切换** — 顶栏 🌙/☀️ 按钮切换深色/浅色模式（服务端持久化）

## 配置持久化

- 登录令牌：`$EPISODE_PATH/token`（Windows 默认 `%USERPROFILE%`，Linux 默认 `/tmp`）
- 服务端设置：`$EPISODE_PATH/episode_renamer.settings.json`（主题、分隔符、是否含集名、TMDB Key 等）
- 旧版连接配置：`$EPISODE_PATH/episode_renamer.conf`

## 依赖

| 依赖                  | 用途                  |
| --------------------- | --------------------- |
| FastAPI + Uvicorn     | Web 服务框架          |
| Vue 3 + Element Plus  | 前端 UI（CDN 引入）   |
| BeautifulSoup4        | TMDB 网页回退解析     |
| requests              | TMDB / OpenList HTTP  |

## 许可证

MIT License