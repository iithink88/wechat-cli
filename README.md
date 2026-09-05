# WeChat CLI 技能包

用**大白话**读取和分析你自己电脑上的微信聊天记录：查会话、搜消息、导出聊天记录、统计活跃度、看收藏。
全程**本地运行**，不联网、不上传，数据不出你的电脑。

---

## 一、三步装好

### 第 1 步：把文件夹放进技能目录

把你拿到的整个 `wechat-cli` 文件夹，复制到你的 WorkBuddy 技能目录：

| 系统 | 技能目录 |
|------|----------|
| Windows | `C:\Users\你的用户名\.workbuddy\skills\` |
| macOS / Linux | `~/.workbuddy/skills/` |

放好后的路径应类似：`...\skills\wechat-cli\SKILL.md`

### 第 2 步：装 wechat-cli 本体

打开终端（Windows 用 PowerShell 或命令提示符）：

```bash
pip install wechat-cli
python --version        # 需 3.10 或以上
wechat-cli --version    # 能输出版本号即成功
```

> 依赖（click / pycryptodome / zstandard）会自动装上。

### 第 3 步：装微信 4.0+ 并登录

- **必须**微信 **4.0 及以上**（3.x 旧版不支持，目录结构和进程名都不一样）
- 官网下载：https://pc.weixin.qq.com/
- **装好后一定要启动微信并扫码登录**，密钥是从微信进程内存里读的，不登录拿不到

然后初始化（微信保持运行）：

```bash
wechat-cli init
```

> **微信 4.1.12 及以上**，`init` 常常提取不到密钥（0 命中），这是正常的。
> 改用随包脚本，一条命令搞定（路径换成你自己的，见下方「找数据目录」）：
> ```bash
> python scripts/extract_keys.py --db-dir "你的db_storage路径" --out ~/.wechat-cli/all_keys.json
> python scripts/set_db_dir.py "你的db_storage路径"
> wechat-cli sessions --limit 5 --format text     # 验证
> ```

**找数据目录**（`<wxid>` 是你自己的微信内部 ID）：

| 系统 | 路径 |
|------|------|
| Windows | `%APPDATA%\Tencent\xwechat\config\*.ini` 指向的目录下 `xwechat_files\<wxid>\db_storage` |
| macOS | `~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/<wxid>/db_storage` |
| Linux | `~/Documents/xwechat_files/<wxid>/db_storage` |

---

## 二、你说什么 → 它做什么

| 你说 | 它会做 |
|------|--------|
| 看看最近有哪些聊天 | `sessions` 列出最近会话 |
| 把我和张三的聊天记录导出来 | `export "张三" --format markdown` |
| 搜一下谁提过"报价" | `search "报价"` |
| 统计这个群这个月的活跃度 | `stats --start-time 2026-09-01` |
| 我有哪些未读消息 | `unread` |
| 看看我收藏的东西 | `favorites` |
| 帮我总结下和李四聊了什么 | 读记录后分类、提炼重点 |
| 换成我另一个微信号 | `python scripts/switch_account.py 1`（需先配 accounts.json） |

完整命令参数见 `references/commands.md`；分析套路见 `references/analysis-guide.md`；
出问题查 `references/troubleshooting.md`。

---

## 三、常见问题

**Q：提示 `Weixin.exe 未运行`，但我微信开着**
你装的是 3.x 旧版（进程名 `WeChat.exe`）。退出旧版，装 4.0+ 新版。

**Q：`wechat-cli init` 提取密钥 0 命中**
微信 4.1+ 不再在内存里缓存明文密钥。用随包的 `scripts/extract_keys.py`（见第 3 步）。

**Q：多个微信号怎么切换**
1. 每个号登录一次，各提取一份密钥：
   `python scripts/extract_keys.py --db-dir "<A的目录>" --out ~/.wechat-cli/all_keys_account1.json`
2. 把 `scripts/accounts.json.example` 复制成 `scripts/accounts.json`，填上你的路径
3. `python scripts/switch_account.py 1` 切换（切换后不用重启微信）

**Q：微信更新后又用不了了**
密钥会变。重新跑一遍 `extract_keys.py` + `set_db_dir.py` 即可。

**Q：导出的聊天记录里有些人导出失败**
`brandsessionholder`、`@placeholder_foldgroup` 是系统占位会话，导出失败属正常。

**Q：macOS 上读不到进程内存**
系统禁止读取其他进程内存，需要对微信做 ad-hoc 重签名，步骤见 `SKILL.md` 的「macOS 安装指引」。

---

## 四、隐私与安全

- 所有数据**仅在本机处理**，脚本不联网、不上传任何信息
- `~/.wechat-cli/all_keys.json` 是你微信数据库的**解密密钥**，等同于微信数据本身，别分享给别人
- 导出的聊天记录含他人隐私，转发前请自行脱敏
- 本包**不含**任何个人数据：原作者的 wxid、数据目录、机器路径均已清除，脚本全部改为命令行传参

## 五、包内结构

```
wechat-cli/
├── SKILL.md                      技能主说明（AI 读这个）
├── README.md                     本文件（人读这个）
├── references/
│   ├── commands.md               完整命令参考
│   ├── analysis-guide.md         消息分析工作流
│   └── troubleshooting.md        故障排查
└── scripts/
    ├── extract_keys.py           4.1.12+ 密钥提取（参数化，通用）
    ├── set_db_dir.py             写入数据库路径配置
    ├── switch_account.py         多账号切换（读 accounts.json）
    ├── accounts.json.example     多账号配置模板
    └── wcdb_key_tool_windows.py  底层库（Windows 内存/密钥校验）
```

---

## 六、来源与改动

- 原技能来自 SkillHub（slug `wechat-cli`，v1.0.1），由原作者发布
- 本分享包在其基础上做了**分享适配**：
  - 删除写死原作者个人 wxid 的一次性调试脚本（`dump_config_blobs.py` / `gen_keys.py`），功能由参数化的 `extract_keys.py` 覆盖
  - 新增 `set_db_dir.py`（写数据库路径配置）、`accounts.json.example`（多账号模板）
  - `switch_account.py` 改为读取 `accounts.json`，不再写死账号
  - 删除 SkillHub 安装器元数据，文档中的作者机器路径改为通用写法
  - 删除"附带微信安装包"的失效说明（本包不含安装包，改为官网下载指引）
