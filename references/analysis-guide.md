# 消息分析工作流指南

本指南介绍如何使用 wechat-cli 进行微信消息的读取与分析，涵盖从简单查询到复杂分析的完整流程。

## 一、环境检查流程

在开始分析之前，先确认环境是否就绪。

### 步骤 1：检查 wechat-cli 是否已安装
```bash
wechat-cli --version
```
如果未安装，执行 `pip install wechat-cli`。

### 步骤 2：检查是否已初始化
```bash
wechat-cli sessions --limit 1
```
- 如果正常返回会话数据 → 已初始化，可以开始使用
- 如果报错 "未找到微信数据目录" → 需要先执行 `wechat-cli init`
- 如果报错 "Weixin.exe 未运行" → 需要先启动微信

### 步骤 3：初始化（仅首次需要）
确保微信正在运行，然后执行：
```bash
wechat-cli init
```
详见 SKILL.md 中的初始化章节。

---

## 二、日常使用场景

### 场景 1：查看最近有什么消息

```bash
# 看最近会话列表
wechat-cli sessions --format text

# 看未读消息
wechat-cli unread --format text
```

### 场景 2：查看某个人的聊天记录

```bash
# 先搜索联系人确认名称
wechat-cli contacts --query "张"

# 查看最近 50 条消息
wechat-cli history "张三" --format text

# 查看今天的消息
wechat-cli history "张三" --start-time "2026-08-05" --format text
```

### 场景 3：搜索特定内容

```bash
# 全局搜索关键词
wechat-cli search "项目方案" --format text

# 在特定群搜索
wechat-cli search "会议" --chat "工作群" --format text

# 搜索特定时间的消息
wechat-cli search "报告" --start-time "2026-08-01" --end-time "2026-08-05" --format text
```

### 场景 4：导出聊天记录备份

```bash
# 导出为 Markdown（推荐，格式更美观）
wechat-cli export "张三" --format markdown --output "张三_聊天记录.md" --limit 100000

# 导出为纯文本
wechat-cli export "AI交流群" --format txt --output "群聊记录.txt" --limit 100000

# 导出指定时间段
wechat-cli export "工作群" --start-time "2026-07-01" --end-time "2026-07-31" --output "7月记录.md" --limit 100000
```

### 场景 5：获取增量新消息（断点续传）

适合定时任务或周期性检查新消息：

```bash
# 第一次调用：返回当前未读消息，并记录位置
wechat-cli new-messages --format text

# 后续调用：只返回上次之后的新消息
wechat-cli new-messages --format text
```

> 状态保存在 `~/.wechat-cli/last_check.json`，删除可重置。

---

## 三、分析工作流

### 流程 A：单次聊天记录分析

适用于"帮我看看和某某的聊天记录"这类需求。

```
1. contacts --query "名称"     → 确认联系人名称
2. history "名称" --limit N    → 读取消息（N 根据需求调整）
3. 分析内容                     → 分类、总结、提取重点
4. stats "名称"                → 可选：获取统计数据辅助分析
```

**消息量参考：**
| 场景 | 建议 --limit |
|------|-------------|
| 快速浏览最近聊天 | 50（默认） |
| 分析一天的消息 | 200-500 |
| 分析一周的消息 | 1000-5000 |
| 完整导出 | 100000 |

### 流程 B：多群消息汇总

适用于"帮我总结一下今天所有群的消息"这类需求。

```
1. sessions --limit 50          → 获取会话列表
2. 筛选出群聊（chat_type 为 group）
3. 对每个群：history "群名" --start-time "今天日期" --limit 10000
4. 汇总分析：分类、总结、提取关键信息
```

### 流程 C：关键词追踪

适用于"帮我找找有没有人提到某某话题"这类需求。

```
1. search "关键词" --format json          → 全局搜索
2. 如果结果太多：加 --chat 限定范围 或 加 --start-time 限定时间
3. 分析搜索结果中的上下文
```

### 流程 D：群聊活跃度分析

适用于"这个群最近活跃吗"这类需求。

```
1. stats "群名" --format text              → 获取统计数据
2. history "群名" --limit 100 --format text → 看最近消息内容
3. members "群名" --format text            → 查看群成员
```

---

## 四、输出格式选择建议

| 场景 | 推荐格式 | 原因 |
|------|----------|------|
| 人眼快速浏览 | `--format text` | 纯文本，直观易读 |
| 程序处理/分析 | `--format json`（默认） | 结构化数据，便于解析 |
| 导出备份 | `export --format markdown` | Markdown 格式，美观且通用 |
| 大量消息阅读 | `export --format txt` | 纯文本，文件体积小 |

---

## 五、JSON 输出结构

### sessions 输出
```json
[
  {
    "chat_name": "显示名称",
    "chat_type": "private|group|official|system",
    "last_message": "最后一条消息摘要",
    "last_time": "YYYY-MM-DD HH:MM:SS",
    "unread_count": 0,
    "message_count": 0
  }
]
```

### history 输出
```json
[
  {
    "time": "YYYY-MM-DD HH:MM:SS",
    "sender": "发送者名称",
    "type": "text|image|voice|...",
    "content": "消息内容",
    "is_self": false,
    "media_path": "媒体文件路径（--media 时才有）"
  }
]
```

### search 输出
```json
[
  {
    "chat_name": "所属聊天",
    "time": "YYYY-MM-DD HH:MM:SS",
    "sender": "发送者",
    "type": "text",
    "content": "匹配的消息内容"
  }
]
```

---

## 六、定时任务集成

如果需要定时执行（如每日消息总结），可结合 `new-messages` 命令：

```bash
# 每日获取新消息（断点续传，不重复）
wechat-cli new-messages --format json
```

在定时任务中的推荐流程：
1. `wechat-cli new-messages` 获取增量消息
2. 对消息按聊天对象分类
3. 对每个聊天的消息进行总结
4. 汇总生成报告
5. 可选：过滤广告/营销消息

---

## 七、性能与限制

| 项目 | 说明 |
|------|------|
| search 最大返回 | 500 条（无法调高，可用 `--offset` 翻页） |
| history 默认返回 | 50 条（可通过 `--limit` 调大） |
| export 默认限制 | 建议显式指定 `--limit 100000` 确保完整导出 |
| 大群消息量大 | 建议用 `--start-time` / `--end-time` 分段查询 |
| 密钥有效期 | 微信更新后可能失效，需 `wechat-cli init --force` 重新提取 |
