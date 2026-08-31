# Book Beats

<div align="center">

**把一本书，变成一张 Spotify 阅读歌单。**

输入书名 → 搜索公开资料 → 生成阅读氛围 → 试听并确认 → 创建私密歌单

[![本地运行](https://img.shields.io/badge/运行方式-本地%20Web%20UI-27483c?style=flat-square)](#三分钟启动)
[![语言](https://img.shields.io/badge/界面-中文%20%2F%20English-d15d43?style=flat-square)](#第一次使用照着做就行)
[![许可证](https://img.shields.io/badge/license-MIT-b8c8b6?style=flat-square)](LICENSE)

</div>

Book Beats 是一个运行在自己电脑上的 Flask 小工具：它会读取书籍相关的公开网页摘要和书评，把文字氛围交给你选择的 AI 模型，再去 Spotify 查找对应歌曲。歌单创建前会先展示试听清单，你可以取消任何不喜欢的歌曲。

> 这是本地应用，不需要部署服务器。Spotify 和 AI 的密钥只在你自己的浏览器与本地进程中使用。

## 你能用它做什么

- **中英双语界面**：首页右上角可切换中文或 English。
- **公开资料辅助选曲**：检索书籍背景、主题、书评和篇幅信息，作为 AI 的参考。
- **多种模型选择**：内置 OpenAI、DeepSeek 预设，也支持其他兼容 OpenAI Chat Completions 的服务。
- **手动或智能歌曲数量**：手动模式可选 1–20 首；智能模式根据篇幅和预计阅读时长推荐，不设人为上限。
- **先预览、后创建**：只有你点击确认后才会创建 Spotify 歌单，未匹配到的歌曲不会加入。
- **默认私密**：歌单默认设为私密，创建后仍可在 Spotify 中调整可见范围。

## 三分钟启动

### 1. 准备软件和账号

你需要：

1. **Python 3.11 或更高版本**。
2. 一个可以创建开发者 App 的 **Spotify 账号**。
3. 一个可调用聊天模型的 **API Key**（OpenAI、DeepSeek 或其他兼容服务均可）。

### 2. 启动 Book Beats

#### Windows（推荐）

双击项目目录中的 [`start_book_beats.bat`](start_book_beats.bat)。脚本会自动：

- 检查或创建项目内的 `.venv` 虚拟环境；
- 安装 [`requirements.txt`](requirements.txt) 中的依赖；
- 启动本地服务并打开浏览器。

如果浏览器没有自动打开，请手动访问：<http://127.0.0.1:5000>

#### macOS / Linux 或 Windows 终端

在项目根目录执行：

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python main.py
```

Windows PowerShell 对应命令：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\main.py
```

然后打开 <http://127.0.0.1:5000>。

## 第一次使用：照着做就行

### 第一步：创建 Spotify App

1. 打开 [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) 并登录。
2. 点击 **Create app** 创建一个应用。
3. 进入应用设置，在 **Redirect URIs** 中添加下面这一行（必须完全一致）：

   ```text
   http://127.0.0.1:5000/callback
   ```

4. 复制应用的 **Client ID** 和 **Client Secret**。它们会填入 Book Beats 首页的 Spotify 区域。

### 第二步：填写模型设置

首页的模型区域提供三个选项：

| 选项 | API 地址（预填） | 模型名（预填） |
| --- | --- | --- |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| DeepSeek | `https://api.deepseek.com` | `deepseek-v4-flash` |
| 其他兼容服务 | 填写服务商提供的地址 | 填写服务商提供的模型名 |

选择预设后仍然可以修改模型名和 API 地址。API 地址需要是完整的 `http://` 或 `https://` 地址，程序会自动请求其 `/chat/completions` 接口。

### 第三步：生成歌单

1. 输入书名，例如 `百年孤独`。
2. 选择歌曲数量：
   - **手动模式**：拖动滑块选择 1–20 首；
   - **智能推荐**：勾选后，由书籍篇幅和预计阅读时长估算数量，适合不知道该选多少首的情况。
3. 点击 **连接 Spotify，开始寻声**，在 Spotify 页面授权。
4. 等待生成页面完成检索、选曲和 Spotify 匹配。通常需要几十秒；模型超时可以直接点击重试。
5. 在预览页试听歌曲，取消不想加入的项目。
6. 点击 **确认创建私密歌单**，完成后打开 Spotify 查看。

## 密钥与隐私

- 表单设置（包括 Spotify Client Secret 和模型 API Key）保存在**当前浏览器的本地存储**中，重启本地服务后仍可恢复。
- OAuth token、公开检索结果和试听预览只保存在运行中的本地进程内，关闭服务后会失效。
- 书名和公开搜索摘要会发送给你填写的模型服务商；Spotify 请求会发送给 Spotify。Book Beats 不提供中转服务器。
- 请只在自己的电脑上使用。用完后点击首页的 **清除本机保存的设置**，或清理浏览器站点数据。
- 当前 Web UI 不要求创建 `.env` 文件。若你希望固定 Flask 会话密钥，可以在 `.env` 中设置 `FLASK_SECRET_KEY`；不要把任何密钥提交到 Git。

## 常见问题

### 双击 bat 后窗口一闪而过

从 PowerShell 运行 `start_book_beats.bat`，可以看到具体错误。最常见原因是没有安装 Python 3.11+，或依赖安装时网络中断。

### 页面提示回调地址错误

确认 Spotify App 中的 Redirect URI 是：

```text
http://127.0.0.1:5000/callback
```

同时确认 Book Beats 仍在运行，并且浏览器地址中的主机是 `127.0.0.1`，不要改成其他地址。

### 模型请求失败或超时

检查 API Key、模型名、API 地址和账户余额；自定义服务需要支持 OpenAI Chat Completions 协议。确认信息后回到生成页面点击重试即可。

### 很多歌曲没有匹配到

这是 Spotify 搜索结果与 AI 推荐曲名不完全一致造成的。可以换用更明确的书名，或在预览页只保留已经匹配到的歌曲。

## 项目结构

```text
book-beats/
├─ main.py                 # Flask 路由、公开检索、模型调用和 Spotify 写入
├─ templates/              # 首页、生成中、预览和结果页面
├─ static/                 # 页面样式与交互脚本
├─ start_book_beats.bat    # Windows 一键启动
├─ requirements.txt        # Python 依赖
└─ test_main.py            # 基础自动化检查
```

## 开发检查

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

## 项目来源与许可证

本项目基于 [MikePenkov/book-beats](https://github.com/MikePenkov/book-beats)，当前 Fork 为 [klein523666/book-beats](https://github.com/klein523666/book-beats)。代码采用 [MIT License](LICENSE) 发布。
