# SimpleDinoWeb（地瓜盒）

一个基于 Flask 的个人站点。内容全部来自本地文件，没有数据库、没有管理后台；日常通过 SSH 维护文件即可。站点主要包括首页、动态、若水的博客、关于、隐藏调试页和友链状态检测。

## 功能概览

- 首页：随机背景音乐、资源列表、友链在线状态、随机句子
- 动态：读取 `static/notice/*.html`，按修改时间倒序插入页面
- 若水的博客：列出 `static/nuoshui/*.pdf`，按修改时间倒序，每页 20 条
- 关于 / 403 / 404 / robots.txt
- 隐藏页：Flask/Python 版本、系统信息、CPU/内存、日志列表（需要 `-e/--extra`）
- 友链心跳：后台线程定期检测 `friendship_links.json` 里的 URL

## 技术栈

- Python 3.10+
- Flask 3.1 / Jinja2
- requests（友链检测）
- psutil（隐藏页系统信息）

## 目录结构

```text
SimpleDinoWeb/
├── app.py                  # Flask 应用与路由
├── README.md
├── requirements.txt
├── friendship_links.json   # 友链列表
├── run.sh / run.bat        # Linux/macOS 与 Windows 启动脚本
├── user_args.txt           # 本地启动参数（由 run 脚本读取）
├── templates/              # Jinja2 模板
└── static/
    ├── css/ js/ images/
    ├── music/              # 随机音乐（*.mp3）
    ├── resource/           # 资源下载
    ├── nuoshui/            # 若水的博客（*.pdf）
    ├── notice/             # 动态 HTML 片段
    └── hidden/             # 运行日志（仅调试）
```

> `static/music/`、`static/resource/`、`static/nuoshui/`、`static/hidden/` 中的大部分内容不会进入 Git（见 `.gitignore`），部署时需要单独同步。仓库里只保留了一首示例音乐。

## 快速开始

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py --debug
```

> Rocky Linux 9.6 默认的 `python3` 是 3.9；Requests 2.33+ 和 Gunicorn 26 都要求 Python 3.10+。建议先安装 `python3.11`（或 3.12），再用它创建虚拟环境，例如 `python3.11 -m venv .venv`。

也可以使用启动脚本：

```bash
./run.sh
```

`run.sh` 会读取 `user_args.txt` 第一行非注释内容作为启动参数；没有该文件时使用脚本里的默认值。日志写入 `static/hidden/latest.log`，启动时会把旧日志轮转为 `run_时间.log`。

> `run.sh` 直接调用 `python3`，不会自动激活 `.venv`；从 systemd 等非交互环境启动时，请确保 PATH 指向虚拟环境，或把脚本中的 `python3` 换成 `.venv/bin/python`。

### Windows

```bat
run.bat
```

同样读取 `user_args.txt`。Windows 下日志由 PowerShell 的 `Tee-Object` 写入 `static\hidden\latest.log`。

## 启动参数

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-i`, `--ip` | 监听地址 | `0.0.0.0` |
| `-p`, `--port` | 监听端口 | `5000` |
| `-d`, `--debug` | 开启 Flask 调试模式 | 关闭 |
| `-e`, `--extra` | 开放 `/hidden` 隐藏页 | 关闭 |
| `-v`, `--version` | 打印版本后退出 | — |
| `-h`, `--help` | 查看帮助 | — |

生产环境按实际部署调整参数，不要长期把 `--debug` 或 `--extra` 暴露在公网。

## 内容维护

站点没有上传接口，所有内容都通过 SSH 直接编辑文件。

### 音乐

把 `.mp3` 文件放进 `static/music/`，首页每次刷新会随机选择一首。当前代码要求该目录至少有一首音乐，否则首页会报错（这是刻意的约束）。

### 资源

把文件放进 `static/resource/`，首页会按文件名排序列出并直接下载。

### 若水的博客

把 PDF 放进 `static/nuoshui/`，页面会按修改时间倒序展示，每页 20 条。

### 动态

在 `static/notice/` 下新增 `.html` 文件，页面会按修改时间倒序把内容整段插入。约定：

- 只写 HTML 片段（`<div>...</div>`），不要带 `<html>`、`<head>`、`<body>`；
- 片段会被原样插入（`|safe`），可以包含 HTML/脚本，因此这个目录只应由管理员通过 SSH 写入；
- 文件名可以随意，排序依据是文件修改时间。

可以参考 `static/notice/example.html`。

### 友链

编辑 `friendship_links.json`，格式：

```json
[
    {
        "name": "浅水咲",
        "url": "https://www.bilibili.com/read/readlist/rl1061728",
        "desc": "🪄喜欢魔法少女请关注B站~"
    }
]
```

- `name` 和 `url` 必须是字符串，`url` 只接受 `http` / `https`；非字符串或空字段会被跳过，无效 URL 会在日志里记录 warning；
- 后台线程每 30 秒（±15 秒抖动）检测一次，每个请求超时 5 秒，最多 4 个并发；
- 修改 JSON 后不需要重启，下一轮检测会自动生效；
- 首次启动到第一轮检测完成前，页面显示 `[未知]`；检测失败显示 `[离线]`。

### 隐藏页与日志

访问 `/hidden` 需要 `-e/--extra`。页面会显示运行环境、CPU/内存和 `static/hidden/` 下的日志列表。

注意：`static/` 是公开静态目录，日志文件可以通过 `/static/hidden/...` 直接访问；`/hidden` 的开关只控制页面本身，不控制静态文件。生产环境建议在 nginx 中禁止访问 `/static/hidden/`，或给 `/hidden` 和日志加上认证/IP 白名单。当前日志目录只适合内网或调试使用。

## 生产部署（Rocky Linux 9.6）

1. 安装 Python 3.10+ 和依赖：
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
   `requirements.txt` 包含应用运行依赖和 Linux/macOS 的 gunicorn（Windows 平台会跳过 gunicorn）。
2. 准备内容目录（`music/resource/nuoshui/notice/hidden`），这些目录的大部分内容不在 Git 中，建议用 `rsync` 同步。
3. 用 systemd 托管应用，前面用 nginx 反向代理；静态文件可以交给 nginx 直接托管。
4. 关闭 `--debug`；如果不需要隐藏页，不要加 `--extra`。

当前代码的两个限制，部署前请留意：

- 友链心跳只在 `python app.py` 的 `__main__` 入口启动。若用 `gunicorn app:app` / `uwsgi` 直接加载应用，心跳不会运行，友链状态会一直是 `[未知]`；需要改造启动入口或另外启动心跳。
- `/hidden` 路由同样依赖 `__main__` 里的启动参数变量；在纯 WSGI 方式下访问会报错。建议后续把开关改成环境变量或 Flask 配置。

如果使用 gunicorn，注意版本对 Python 的要求（requirements 中固定的 gunicorn 26.x 需要 Python 3.10+）。

## 开发提示

- 所有页面模板都各自包含头部和底部，目前没有抽成 `base.html`；改导航/页脚时需要同步修改多个模板。
- 修改 `friendship_links.json`、`notice`、`music`、`nuoshui` 都不需要重启应用（模板/代码改动除外）。
- `.gitignore` 已忽略 `__pycache__/`、`*.py[cod]`、`.DS_Store` 和大部分内容目录。
- `user_args.txt` 目前仍被 Git 跟踪；如果希望它只存在于本机，执行 `git rm --cached user_args.txt`。
- 项目当前未包含测试文件和测试依赖；如需测试，请自行安装 `pytest`。

## 相关链接

- 项目源码：<https://github.com/MENGDU123/SimpleDinoWeb>
- 作者：Cream_MENGDU / 奶酪糖·梦都
