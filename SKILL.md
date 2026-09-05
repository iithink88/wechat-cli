---
name: wechat-cli
description: 通过 wechat-cli 读取和分析微信聊天记录。当用户想查看、搜索、导出或分析微信消息、联系人、收藏时调用此技能。
slug: wechat-cli
version: 1.0.1
displayName: 通过 wechat-cli 读取和分析微信聊天记录
---

# WeChat CLI — 微信聊天记录读取与分析

本技能通过 `wechat-cli` 命令行工具，帮助用户读取和分析本地微信的聊天记录、联系人、收藏等数据。支持会话浏览、消息搜索、聊天记录导出、统计分析等功能。

## 适用场景

- 查看最近会话列表 / 未读消息
- 查看指定联系人或群聊的聊天记录
- 按关键词搜索消息
- 导出聊天记录为 Markdown 或纯文本
- 聊天统计分析（消息数量、活跃度等）
- 查看微信收藏
- 获取增量新消息（断点续传）
- 对聊天记录进行分类总结、重点提取等分析任务

## 前置条件

### 系统支持
- Windows（Weixin.exe）
- macOS（WeChat）
- Linux（wechat）

### 必须满足
1. **使用微信 4.0 及以上版本** — wechat-cli 仅兼容微信 4.0+ 新版架构，不支持 3.x 旧版。请自行到 https://pc.weixin.qq.com/ 下载安装（本包不含微信安装包）
2. **微信客户端已安装并登录** — 工具读取本地微信数据库，微信必须已登录
3. **初始化时微信必须处于运行状态** — 密钥提取需要扫描微信进程内存
4. **Python 3.10+** — wechat-cli 是 Python 工具

### 微信安装（重要）

wechat-cli **仅支持微信 4.0 及以上版本**，不支持微信 3.x 旧版。

**为什么需要 4.0+：**
- 微信 4.0 采用了全新的跨平台架构，进程名从 `WeChat.exe` 变为 `Weixin.exe`（Windows），数据目录从 `WeChat Files` 变为 `xwechat_files`
- wechat-cli 的密钥提取逻辑针对 4.0 架构设计，无法识别 3.x 版本的进程和数据库

> **注意**：本分享包**不含**微信安装包（体积过大且涉及版权）。请自行安装微信 **4.0 及以上版本**，
> 官方下载：https://pc.weixin.qq.com/ 。装好并登录后，再按下方步骤操作。

| 平台 | 要求 | 进程名 | 数据根目录 |
|------|------|--------|-----------|
| Windows | 微信 4.0+ | `Weixin.exe` | 见下方路径表 |
| macOS | 微信 4.0+ | `WeChat` | `~/Library/Containers/com.tencent.xinWeChat/Data/Documents/` |
| Linux | 微信 4.0+ | `wechat` | `~/Documents/` |

#### Windows 安装指引

1. **下载并安装**微信 4.0+（https://pc.weixin.qq.com/ ）
2. **运行微信**并**扫码登录**
3. 确认微信已完全启动并登录后，再执行初始化（见下方「初始化」）

> 若电脑上已有旧版微信（3.x），先退出旧版再装新版。旧版数据目录是 `WeChat Files`，
> 与 4.0+ 的 `xwechat_files` 不同，wechat-cli 无法识别。

#### macOS 安装指引

**第一步：安装微信**

1. **打开 DMG 文件**：双击从官网下载的微信 DMG，系统会挂载一个磁盘镜像
2. **安装微信**：在弹出的窗口中，将左侧的 **WeChat** 图标拖拽到右侧的 **Applications（应用程序）** 文件夹
3. **弹出 DMG**：安装完成后，在 Finder 侧边栏点击 DMG 磁盘旁的弹出按钮，卸载镜像

**第二步：重新签名 WeChat（必须）**

macOS 默认禁止读取其他进程内存，需要对微信进行 ad-hoc 重签名，wechat-cli 才能提取密钥。

1. **打开终端**：在「启动台」搜索「终端」或「Terminal」并打开
2. **提取微信原有权限**：
```bash
codesign -d --entitlements - --xml /Applications/WeChat.app > ~/wechat_ent.plist
```
3. **复制 WeChat 到用户目录**（推荐，最安全）：
```bash
rm -rf ~/Applications/WeChat.app
cp -R /Applications/WeChat.app ~/Applications/
```
4. **对副本进行签名**：
```bash
codesign --force --deep --sign - --entitlements ~/wechat_ent.plist ~/Applications/WeChat.app
```
5. **以后运行这个副本**：
```bash
open ~/Applications/WeChat.app
```

**第三步：登录并初始化**

1. **打开微信**：运行上一步签名后的副本（`~/Applications/WeChat.app`）
2. **处理安全提示**：首次打开可能提示"无法验证开发者"或"来自身份不明的开发者"：
   - 点击 **取消**
   - 进入 **系统设置 → 隐私与安全性**，找到关于 WeChat 的安全提示，点击 **仍要打开**
   - 再次打开 WeChat，点击 **打开**
3. **扫码登录**：用手机微信扫码登录
4. 确认微信已完全启动并登录后，执行初始化：
```bash
sudo wechat-cli init --force
```

> **为什么需要重新签名？** macOS 出于安全考虑，禁止进程读取其他进程的内存。wechat-cli 需要扫描微信进程内存来提取数据库解密密钥，因此必须对微信进行 ad-hoc 重签名以放开此限制。
>
> **注意**：微信更新后需要重新签名。每次微信自动更新后，重复上述第二步即可。

#### 已安装旧版微信怎么办？

如果电脑上已经安装了旧版微信（3.x），需要先卸载或退出旧版，再装 4.0+ 新版。**退出正在运行的旧版微信后再启动新版**。

> **重要**：必须是 **4.0 及以上**。3.x 旧版用了另一套目录结构（`WeChat Files`）和进程名（`WeChat.exe`），
> wechat-cli 完全无法识别。另外，不同 4.x 小版本的内存布局有差异，若密钥提取 0 命中，
> 换一个 4.x 版本往往就好了（见 `references/troubleshooting.md`）。

## 安装

```bash
pip install wechat-cli
```

依赖包（自动安装）：`click`、`pycryptodome`、`zstandard`

安装完成后验证：
```bash
wechat-cli --version
# 输出: wechat-cli, version 0.2.4
```

## 初始化（首次使用必读）

初始化会提取微信数据库的加密密钥并生成配置文件。**只需执行一次**。

### 步骤

1. **确保微信正在运行且已登录**（这是必须的，密钥从微信进程内存中提取）

2. **执行初始化命令**：
```bash
wechat-cli init
```
工具会自动：
- 检测微信数据目录
- 扫描微信进程内存提取数据库密钥
- 在 `~/.wechat-cli/` 下生成 `config.json` 和 `all_keys.json`

3. **如果自动检测失败**，手动指定数据目录：
```bash
wechat-cli init --db-dir "C:\path\to\db_storage"
```

### 微信数据目录位置参考

| 系统 | 默认路径 |
|------|----------|
| Windows | `%APPDATA%\Tencent\xwechat\config\*.ini` 指向的目录下 `xwechat_files\<wxid>\db_storage` |
| macOS | `~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/<wxid>/db_storage` |
| Linux | `~/Documents/xwechat_files/<wxid>/db_storage` |

> **提示**：`<wxid>` 是你的微信内部 ID，类似 `wxid_xxxxxxxxxxxxx`。

### 重新初始化

如果密钥过期（如微信更新后），强制重新提取：
```bash
wechat-cli init --force
```

### 配置文件说明

初始化后，配置保存在 `~/.wechat-cli/` 目录：

| 文件 | 说明 |
|------|------|
| `config.json` | 主配置，记录 `db_dir`（数据库路径） |
| `all_keys.json` | 数据库解密密钥 |
| `last_check.json` | `new-messages` 命令的状态文件（记录上次读取位置） |

## 快速入门

### 1. 查看最近会话
```bash
wechat-cli sessions
```

### 2. 查看某人的聊天记录
```bash
wechat-cli history "张三" --limit 20
```

### 3. 搜索消息
```bash
wechat-cli search "关键词"
```

### 4. 查看未读会话
```bash
wechat-cli unread
```

### 5. 导出聊天记录
```bash
wechat-cli export "张三" --format markdown --output chat.md
```

## 命令总览

| 命令 | 说明 | 常用参数 |
|------|------|----------|
| `init` | 初始化（提取密钥） | `--db-dir`, `--force` |
| `sessions` | 最近会话列表 | `--limit`, `--format` |
| `history` | 指定聊天的消息记录 | `--limit`, `--offset`, `--start-time`, `--end-time`, `--type`, `--media` |
| `search` | 搜索消息内容 | `--chat`, `--start-time`, `--end-time`, `--limit`, `--type` |
| `contacts` | 搜索/列出联系人 | `--query`, `--detail`, `--limit` |
| `export` | 导出聊天记录 | `--format`, `--output`, `--start-time`, `--end-time`, `--limit` |
| `members` | 群聊成员列表 | `--format` |
| `stats` | 聊天统计分析 | `--start-time`, `--end-time`, `--format` |
| `unread` | 未读会话 | `--limit`, `--format` |
| `new-messages` | 增量新消息 | `--format` |
| `favorites` | 微信收藏 | `--type`, `--query`, `--limit`, `--format` |

> 完整命令参数详见 `references/commands.md`

## 输出格式

大多数命令支持 `--format` 参数：
- `json`（默认）— 结构化 JSON，适合程序处理
- `text` — 纯文本，适合人类阅读

时间格式：`YYYY-MM-DD` 或 `YYYY-MM-DD HH:MM:SS`

消息类型过滤（`--type`）：`text`、`image`、`voice`、`video`、`sticker`、`location`、`link`、`file`、`call`、`system`

## 重要注意事项

- **默认限制**：`history` 默认返回 50 条，`search` 最大 500 条，`sessions` 默认 20 个。导出大量数据时用 `--limit 100000`
- **系统占位会话**：`brandsessionholder`、`@placeholder_foldgroup` 是系统占位符，导出时会失败，属正常现象
- **隐私安全**：所有数据仅在本地处理，不会上传任何信息
- **微信需运行**：虽然查询操作不需要微信运行，但初始化（密钥提取）必须微信在线

## 分析工作流

当用户需要分析聊天记录时，推荐工作流详见 `references/analysis-guide.md`。

典型流程：
1. `sessions` — 浏览会话列表，确定分析对象
2. `history` — 读取目标聊天的消息记录
3. 对消息内容进行分类、总结、提取重点
4. 如需深度分析，用 `stats` 获取统计数据辅助

## 故障排查

常见问题及解决方案详见 `references/troubleshooting.md`。

## 微信 4.1.12+ 密钥提取（重要适配，2026-08-10 实测）

> **背景**：微信 4.1+ 不再在进程内存缓存明文密钥（`x'...'` 格式），`wechat-cli init` 的内存扫描在 4.1+ 上 0 命中属正常。wx_key（DLL 注入工具）已被 DMCA 下架，GitHub release 全删。实测发现：**4.1.12 的 `com.Tencent.WCDB.Config.Cipher` 对象里存的是每个数据库的（派生后密钥 32B + salt 16B）十六进制对，密钥可直接用于解密，无需 PBKDF2**。

### 前提
- 微信 4.1.12+ 正在运行且已登录
- **必须确认当前登录账号与目标 db_storage 目录一致**（多开/多账号环境：内存里的密钥属于当前登录账号！）
- Python 3.10+，且已 `pip install wechat-cli`
- Windows 下需要能读取微信进程内存（普通权限通常即可；若失败用管理员权限重跑）

### 步骤（一条命令提取密钥，无需改脚本）
1. **提取密钥**（把路径换成你自己的 db_storage）：
   ```
   python scripts/extract_keys.py --db-dir "你的db_storage路径" --out ~/.wechat-cli/all_keys.json
   ```
   脚本会自动 dump `Weixin.exe` 内存中 `com.Tencent.WCDB.Config.Cipher` 的 blob，
   对其中 64~192 位 hex 串取 32B 窗口，用 HMAC 校验匹配数据库 salt，成功即写入密钥文件。
2. **写入数据库路径**（extract_keys.py 只管密钥，路径要单独写）：
   ```
   python scripts/set_db_dir.py "你的db_storage路径"
   ```
   生成 `~/.wechat-cli/config.json`，内容形如 `{"db_dir": "..."}`
3. **验证**：
   ```
   wechat-cli sessions --limit 5 --format text
   ```

### 已知限制
- 实测 16/18 库成功；`message\weclaw.db`、`solitaire\solitaire.db` 未提取到（非核心库，不影响聊天记录查询）
- 微信重启/更新后密钥可能变化，需重新执行上述步骤
- 若 Config.Cipher 扫描 nodes=0：微信版本过新或进程选择错误，先确认登录账号
- 密钥对是 (key+salt)，**直接当加密密钥用，不要做 PBKDF2 派生**（那是 4.1.x 早期版本的 passphrase 路线）

### 你的环境速查（首次跑通后自行记录）
- wechat-cli 可执行文件：装完后用 `where wechat-cli`（Windows）或 `which wechat-cli`（macOS/Linux）查
- Python：用 `python --version` 确认 ≥ 3.10
- 配置目录：`~/.wechat-cli/`（`all_keys.json` 密钥 / `config.json` 路径 / `last_check.json` 增量状态）
- 数据目录：见上方「微信数据目录位置参考」表，`<wxid>` 换成你自己的

### 多账号用法
1. 逐个账号提取密钥（每换一个账号登录，就跑一次）：
   ```
   python scripts/extract_keys.py --db-dir "账号A的db_storage" --out ~/.wechat-cli/all_keys_account1.json
   python scripts/extract_keys.py --db-dir "账号B的db_storage" --out ~/.wechat-cli/all_keys_account2.json
   ```
2. 把 `scripts/accounts.json.example` 复制为 `scripts/accounts.json`，填上每个账号的 `db` 和 `key`
3. 切换：
   ```
   python scripts/switch_account.py            # 列出账号
   python scripts/switch_account.py 1          # 切到 1 号（同时复制密钥 + 写 config.json）
   ```
   切换后无需重启微信（查询只读数据库）

## 参考文档

- [完整命令参考](references/commands.md)
- [消息分析工作流指南](references/analysis-guide.md)
- [常见问题排查](references/troubleshooting.md)
