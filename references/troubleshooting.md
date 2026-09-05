# 常见问题排查

## 微信版本问题

### Q: 我应该用哪个版本的微信？

wechat-cli **仅支持微信 4.0 及以上版本**，微信 3.x 旧版不兼容。

> 本分享包**不含**微信安装包，请到官网自行下载安装：https://pc.weixin.qq.com/
> 若某个 4.x 版本密钥提取 0 命中，换一个 4.x 版本通常就好了（内存布局有差异）。

**判断当前微信版本：**
- 打开微信 → 设置 → 关于微信，查看版本号
- Windows：4.0+ 版本的进程名是 `Weixin.exe`，3.x 版本是 `WeChat.exe`
- 数据目录：4.0+ 是 `xwechat_files`，3.x 是 `WeChat Files`

### Q: 报错 "Weixin.exe 未运行" 但我的微信明明开着

**原因**：你可能使用的是微信 3.x 旧版，其进程名是 `WeChat.exe` 而非 `Weixin.exe`，wechat-cli 无法识别。

**解决**：
1. 退出当前正在运行的旧版微信
2. 到 https://pc.weixin.qq.com/ 下载安装 **4.0+** 版本
   - **Windows**：安装后确认任务管理器里进程名是 `Weixin.exe`
   - **macOS**：安装后确认是新版 `/Applications/WeChat.app`
3. 登录微信后，重新执行初始化（`wechat-cli init`，4.1.12+ 见 SKILL.md 的密钥提取章节）

### Q: Windows 上安装微信

1. 退出当前正在运行的微信（如有）
2. 从 https://pc.weixin.qq.com/ 下载并安装微信 4.0+
3. 启动微信，用手机扫码登录
4. 确认微信完全启动后，执行初始化

### Q: macOS 上安装微信

1. 双击官网下载的微信 DMG 挂载磁盘镜像
2. 在弹出窗口中，将 WeChat 图标拖拽到 Applications（应用程序）文件夹
3. 在 Finder 侧边栏弹出 DMG 磁盘
4. **重新签名 WeChat（必须）**：打开终端，执行以下命令：
```bash
# 提取微信原有权限
codesign -d --entitlements - --xml /Applications/WeChat.app > ~/wechat_ent.plist

# 复制到用户目录（推荐，最安全）
rm -rf ~/Applications/WeChat.app
cp -R /Applications/WeChat.app ~/Applications/

# 签名副本
codesign --force --deep --sign - --entitlements ~/wechat_ent.plist ~/Applications/WeChat.app

# 以后运行这个副本
open ~/Applications/WeChat.app
```
5. **处理安全提示**：首次打开可能提示"无法验证开发者"：
   - 点击 **取消**
   - 进入 **系统设置 → 隐私与安全性**，找到 WeChat 安全提示，点击 **仍要打开**
   - 再次打开 WeChat，点击 **打开**
6. 用手机微信扫码登录
7. 确认微信完全启动后，执行初始化：
```bash
sudo wechat-cli init --force
```

### Q: macOS 上 wechat-cli init 提示权限不足或无法读取微信内存

**原因**：macOS 默认禁止进程读取其他进程内存，需要对微信进行 ad-hoc 重签名。

**解决**：按上方「macOS 上安装微信」的第 4 步重新签名微信，然后重新执行 `sudo wechat-cli init --force`。

### Q: macOS 上微信更新后 wechat-cli 失效

**原因**：微信自动更新后签名会恢复为官方签名，wechat-cli 无法读取内存。

**解决**：重新执行签名步骤：
```bash
codesign -d --entitlements - --xml /Applications/WeChat.app > ~/wechat_ent.plist
codesign --force --deep --sign - --entitlements ~/wechat_ent.plist ~/Applications/WeChat.app
```
然后重新执行 `sudo wechat-cli init --force`。

---

## 初始化问题

### Q: 执行 `wechat-cli init` 报错 "Weixin.exe 未运行"

**原因**：密钥提取需要扫描微信进程内存，微信必须处于运行状态。

**解决**：
1. 打开微信客户端并登录
2. 确认微信进程正在运行（Windows 任务管理器中可见 `Weixin.exe`）
3. **确认微信版本为 4.0+**（3.x 版本的进程名是 `WeChat.exe`，不兼容）
4. 重新执行 `wechat-cli init`

### Q: "未能自动检测到微信数据目录"

**原因**：自动检测失败，可能是微信安装在非默认路径。

**解决**：
1. 手动查找数据目录：
   - **Windows**：打开 `%APPDATA%\Tencent\xwechat\config\`，读取其中的 `.ini` 文件内容（即数据根路径），然后在 `<根路径>\xwechat_files\<wxid>\db_storage` 找到数据库
   - **macOS**：`~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/<wxid>/db_storage`
   - **Linux**：`~/Documents/xwechat_files/<wxid>/db_storage`
2. 手动指定路径：
```bash
wechat-cli init --db-dir "完整路径/db_storage"
```

### Q: "密钥提取失败" 或 "未能从任何微信进程中提取到密钥"

**原因**：可能是微信版本不兼容、权限不足、或微信刚启动密钥尚未加载到内存。

**解决**：
1. **确认微信版本为 4.0+**（3.x 版本不兼容，需升级）
2. 确保微信已完全启动并登录（等待 1-2 分钟让密钥加载到内存）
3. 以管理员权限运行命令行（Windows: 右键 → 以管理员身份运行）
4. 尝试强制重新提取：
```bash
wechat-cli init --force
```
4. 如果仍然失败，可能是微信版本更新导致兼容性问题

### Q: 微信更新后查询报错

**原因**：微信更新后数据库密钥可能已变更。

**解决**：
```bash
wechat-cli init --force
```
重新提取密钥即可。

---

## 查询问题

### Q: 执行查询命令报错 "未找到微信数据目录"

**原因**：尚未初始化，或配置文件损坏。

**解决**：
1. 检查配置文件是否存在：`~/.wechat-cli/config.json`
2. 如果不存在，执行初始化：`wechat-cli init`
3. 如果存在但内容有误，删除后重新初始化：
```bash
rm ~/.wechat-cli/config.json
rm ~/.wechat-cli/all_keys.json
wechat-cli init
```

### Q: `history` 命令找不到联系人

**原因**：传入的名称与微信中的显示名称不匹配。

**解决**：
1. 先用 `contacts` 搜索确认正确名称：
```bash
wechat-cli contacts --query "张"
```
2. 使用返回的精确名称查询：
```bash
wechat-cli history "精确名称" --format text
```
3. 也可以尝试用备注名或 wxid

### Q: 查询返回空结果

**可能原因及解决**：
1. **消息量不足**：该聊天可能消息较少，尝试去掉 `--limit` 使用默认值
2. **时间范围不对**：检查 `--start-time` / `--end-time` 是否正确
3. **名称不匹配**：用 `contacts` 确认名称
4. **类型过滤太严**：去掉 `--type` 参数看看是否有其他类型的消息
5. **系统占位会话**：`brandsessionholder`、`@placeholder_foldgroup` 是系统占位符，无实际消息

### Q: `export` 导出的消息不完整

**原因**：默认导出可能有数量限制。

**解决**：
```bash
wechat-cli export "名称" --limit 100000 --format markdown --output output.md
```
显式指定 `--limit 100000` 确保完整导出。

### Q: `search` 最多只能返回 500 条

**原因**：`search` 命令的 `--limit` 最大值为 500，这是设计限制。

**解决**：使用 `--offset` 翻页获取更多结果：
```bash
# 第一页
wechat-cli search "关键词" --limit 500 --offset 0

# 第二页
wechat-cli search "关键词" --limit 500 --offset 500
```

或者缩小搜索范围（用 `--chat` 限定聊天对象，或用 `--start-time` 限定时间）。

---

## 权限问题

### Q: Windows 上 "无法打开进程" 警告

**原因**：权限不足，无法读取微信进程内存。

**解决**：以管理员身份运行命令行（PowerShell / CMD 右键 → 以管理员身份运行）。

### Q: macOS/Linux 上需要 sudo 权限

**原因**：读取其他进程内存需要 root 权限。

**解决**：
```bash
sudo wechat-cli init
```

---

## 安装问题

### Q: `pip install wechat-cli` 失败

**解决**：
1. 确保 pip 是最新版本：`pip install --upgrade pip`
2. 尝试使用国内镜像源：
```bash
pip install wechat-cli -i https://pypi.tuna.tsinghua.edu.cn/simple
```
3. 如果依赖安装失败，单独安装依赖：
```bash
pip install click pycryptodome zstandard
```

### Q: 安装后 `wechat-cli` 命令找不到

**原因**：Python Scripts 目录未加入 PATH。

**解决**：
1. 找到 wechat-cli 的安装位置：
```bash
pip show wechat-cli
```
2. 在 `Location` 路径的同级 `Scripts` 目录下找到 `wechat-cli.exe`（Windows）或 `wechat-cli`（macOS/Linux）
3. 将该 Scripts 目录添加到系统 PATH，或直接使用完整路径调用

### Q: `wechat-cli` 命令在 PowerShell 中不识别

**原因**：PowerShell 可能未刷新 PATH。

**解决**：
1. 关闭并重新打开 PowerShell
2. 或使用完整路径：
```powershell
& "C:\path\to\Python\Scripts\wechat-cli.exe" sessions
```

---

## 其他问题

### Q: `new-messages` 返回的消息不正确或重复

**原因**：状态文件 `last_check.json` 可能损坏。

**解决**：
```bash
# 删除状态文件重置
rm ~/.wechat-cli/last_check.json

# 重新调用
wechat-cli new-messages
```

### Q: JSON 输出中有乱码

**原因**：终端编码问题。

**解决**：
1. Windows PowerShell 设置 UTF-8 编码：
```powershell
chcp 65001
```
2. 或将输出重定向到文件后用编辑器打开：
```bash
wechat-cli sessions --format json > sessions.json
```

### Q: 导出的 Markdown 文件中文乱码

**解决**：确保用 UTF-8 编码打开文件。大多数现代编辑器（VS Code、Typora、Obsidian）默认使用 UTF-8。
