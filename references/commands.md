# wechat-cli 完整命令参考

本文档列出 wechat-cli v0.2.4 的所有命令及其完整参数。

## 全局选项

```
wechat-cli [OPTIONS] COMMAND [ARGS]...
```

| 选项 | 说明 |
|------|------|
| `--version` | 显示版本号 |
| `--config TEXT` | 指定 config.json 路径（默认自动查找 `~/.wechat-cli/config.json`） |
| `--help` | 显示帮助 |

也可通过环境变量 `WECHAT_CLI_CONFIG` 指定配置路径。

---

## init — 初始化

提取微信数据库密钥并生成配置。**首次使用必须执行，且微信必须正在运行。**

```
wechat-cli init [OPTIONS]
```

| 选项 | 类型 | 说明 |
|------|------|------|
| `--db-dir TEXT` | 路径 | 微信数据目录路径（默认自动检测） |
| `--force` | 标志 | 强制重新提取密钥（密钥过期时使用） |

### 示例
```bash
# 自动检测
wechat-cli init

# 手动指定数据目录
wechat-cli init --db-dir "E:\xwechat_files\wxid_xxx\db_storage"

# 强制重新提取（微信更新后密钥失效）
wechat-cli init --force
```

### 初始化输出
```
WeChat CLI 初始化
========================================
[+] 检测到微信数据目录: E:\xwechat_files\wxid_xxx\db_storage

开始提取密钥...
============================================================
  提取所有微信数据库密钥
============================================================
找到 N 个数据库, M 个不同的salt
[+] Weixin.exe PID=12345 (500MB)
...
[+] 初始化完成!
    配置: ~/.wechat-cli/config.json
    密钥: ~/.wechat-cli/all_keys.json
    提取到 N 个数据库密钥
```

---

## sessions — 最近会话列表

获取最近的聊天会话列表。

```
wechat-cli sessions [OPTIONS]
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--limit INTEGER` | 数量 | 20 | 返回的会话数量 |
| `--format` | json/text | json | 输出格式 |

### 示例
```bash
wechat-cli sessions                          # 最近 20 个会话 (JSON)
wechat-cli sessions --limit 10               # 最近 10 个会话
wechat-cli sessions --format text            # 纯文本输出
wechat-cli sessions --limit 50 --format text # 最近 50 个，纯文本
```

### JSON 输出字段
```json
[
  {
    "chat_name": "张三",
    "chat_type": "private",
    "last_message": "好的，明天见",
    "last_time": "2026-08-05 14:30:00",
    "unread_count": 3,
    "message_count": 1250
  }
]
```

---

## history — 聊天消息记录

获取指定联系人或群聊的消息记录。

```
wechat-cli history [OPTIONS] CHAT_NAME
```

`CHAT_NAME` 是联系人昵称、备注或群名（**必须用引号包裹**）。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--limit INTEGER` | 数量 | 50 | 返回的消息数量 |
| `--offset INTEGER` | 偏移 | 0 | 分页偏移量 |
| `--start-time TEXT` | 时间 | 无 | 起始时间 `YYYY-MM-DD [HH:MM[:SS]]` |
| `--end-time TEXT` | 时间 | 无 | 结束时间 `YYYY-MM-DD [HH:MM[:SS]]` |
| `--format` | json/text | json | 输出格式 |
| `--type` | 类型 | 无 | 消息类型过滤（见下表） |
| `--media` | 标志 | 否 | 解析媒体文件路径（图片/文件/视频/语音） |

### 消息类型
| 值 | 说明 |
|----|------|
| `text` | 文本消息 |
| `image` | 图片 |
| `voice` | 语音 |
| `video` | 视频 |
| `sticker` | 表情包 |
| `location` | 位置 |
| `link` | 链接/卡片 |
| `file` | 文件 |
| `call` | 通话 |
| `system` | 系统消息 |

### 示例
```bash
# 最近 50 条消息（默认）
wechat-cli history "张三"

# 最近 100 条，偏移 50（即第 51-150 条）
wechat-cli history "张三" --limit 100 --offset 50

# 指定时间范围
wechat-cli history "AI交流群" --start-time "2026-04-01" --end-time "2026-04-02"

# 纯文本输出
wechat-cli history "张三" --format text

# 只看文本消息
wechat-cli history "张三" --type text --limit 100

# 解析媒体路径（查看图片/文件等的具体位置）
wechat-cli history "张三" --media --limit 50

# 大量消息导出
wechat-cli history "AI交流群" --limit 100000 --format text
```

---

## search — 搜索消息

按关键词搜索消息内容，可全局搜索或限定聊天对象。

```
wechat-cli search [OPTIONS] KEYWORD
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--chat TEXT` | 名称 | 无 | 限定聊天对象（**可多次指定**搜索多个群/人） |
| `--start-time TEXT` | 时间 | 无 | 起始时间 |
| `--end-time TEXT` | 时间 | 无 | 结束时间 |
| `--limit INTEGER` | 数量 | 500 | 返回数量（**最大 500**） |
| `--offset INTEGER` | 偏移 | 0 | 分页偏移量 |
| `--format` | json/text | json | 输出格式 |
| `--type` | 类型 | 无 | 消息类型过滤 |

### 示例
```bash
# 全局搜索
wechat-cli search "Claude"

# 在指定群搜索
wechat-cli search "Claude" --chat "AI交流群"

# 同时搜多个群
wechat-cli search "开会" --chat "群A" --chat "群B"

# 带时间范围
wechat-cli search "你好" --start-time "2026-04-01" --limit 50

# 纯文本输出
wechat-cli search "项目" --format text --limit 100
```

---

## contacts — 联系人

搜索或查看联系人详情。

```
wechat-cli contacts [OPTIONS]
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--query TEXT` | 关键词 | 无 | 搜索关键词（匹配昵称、备注、wxid） |
| `--detail TEXT` | 名称 | 无 | 查看联系人详情（传入昵称/备注/wxid） |
| `--limit INTEGER` | 数量 | 无 | 返回数量 |
| `--format` | json/text | json | 输出格式 |

### 示例
```bash
# 搜索联系人
wechat-cli contacts --query "李"

# 查看联系人详情
wechat-cli contacts --detail "张三"

# 通过 wxid 查看
wechat-cli contacts --detail "wxid_xxxxxxxxxxxxx"
```

---

## export — 导出聊天记录

将聊天记录导出为 Markdown 或纯文本文件。

```
wechat-cli export [OPTIONS] CHAT_NAME
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--format` | markdown/txt | markdown | 导出格式 |
| `--output TEXT` | 路径 | stdout | 输出文件路径（不指定则输出到终端） |
| `--start-time TEXT` | 时间 | 无 | 起始时间 |
| `--end-time TEXT` | 时间 | 无 | 结束时间 |
| `--limit INTEGER` | 数量 | 无 | 导出消息数量 |

### 示例
```bash
# 导出为 Markdown
wechat-cli export "张三" --format markdown --output "张三.md"

# 导出为纯文本
wechat-cli export "AI交流群" --format txt --output group.txt

# 带时间范围导出
wechat-cli export "张三" --start-time "2026-04-01" --end-time "2026-04-30" --output april.md

# 导出大量消息（注意 limit）
wechat-cli export "AI交流群" --limit 100000 --format markdown --output all.md
```

> **重要**：不指定 `--limit` 时导出数量可能受限。完整导出请加 `--limit 100000`。

---

## members — 群聊成员

查询群聊成员列表。

```
wechat-cli members [OPTIONS] GROUP_NAME
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--format` | json/text | json | 输出格式 |

### 示例
```bash
wechat-cli members "AI交流群"
wechat-cli members "群名" --format text
```

---

## stats — 聊天统计

对指定聊天进行统计分析。

```
wechat-cli stats [OPTIONS] CHAT_NAME
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--start-time TEXT` | 时间 | 无 | 起始时间 |
| `--end-time TEXT` | 时间 | 无 | 结束时间 |
| `--format` | json/text | json | 输出格式 |

### 示例
```bash
# 整体统计
wechat-cli stats "AI交流群"

# 指定时间范围
wechat-cli stats "张三" --start-time "2026-04-01" --end-time "2026-04-03"

# 纯文本输出
wechat-cli stats "群名" --format text
```

---

## unread — 未读会话

查看有未读消息的会话。

```
wechat-cli unread [OPTIONS]
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--limit INTEGER` | 数量 | 无 | 返回的会话数量 |
| `--format` | json/text | json | 输出格式 |

### 示例
```bash
wechat-cli unread                       # 所有未读会话
wechat-cli unread --limit 10            # 最多 10 个
wechat-cli unread --format text         # 纯文本
```

---

## new-messages — 增量新消息

获取自上次调用以来的新消息。支持断点续传。

```
wechat-cli new-messages [OPTIONS]
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--format` | json/text | json | 输出格式 |

### 状态文件
`~/.wechat-cli/last_check.json` — 记录上次读取位置。删除此文件可重置。

### 示例
```bash
# 首次调用：返回未读消息并记录状态
wechat-cli new-messages

# 再次调用：仅返回新增消息
wechat-cli new-messages

# 纯文本输出
wechat-cli new-messages --format text
```

---

## favorites — 微信收藏

查看微信收藏内容。

```
wechat-cli favorites [OPTIONS]
```

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--limit INTEGER` | 数量 | 无 | 返回数量 |
| `--type` | 类型 | 无 | 按类型过滤：`text`/`image`/`article`/`card`/`video` |
| `--query TEXT` | 关键词 | 无 | 关键词搜索 |
| `--format` | json/text | json | 输出格式 |

### 示例
```bash
# 最近收藏
wechat-cli favorites

# 只看文章
wechat-cli favorites --type article

# 搜索收藏
wechat-cli favorites --query "计算机网络"

# 限制数量 + 纯文本
wechat-cli favorites --limit 5 --format text
```
