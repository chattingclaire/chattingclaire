# Mac快速开始 - "180K - 星球讨论群🪙"

Mac电脑最简单的使用方法。

---

## 🍎 最简单方法（5分钟搞定）

### 步骤1：从Mac微信复制消息

1. 打开**微信Mac客户端**
2. 进入 **"180K - 星球讨论群🪙"**
3. 选择今天的消息：
   - 按住 `Cmd` 键
   - 点击选择多条消息
4. 按 `Cmd+C` 复制

### 步骤2：粘贴并格式化

```bash
# 运行格式化工具
cd ~/chattingclaire
python tools/format_wechat_paste.py

# 粘贴你复制的内容 (Cmd+V)
# 按 Ctrl+D 完成输入
# 工具会自动格式化并保存
```

### 步骤3：完成！

文件会自动保存到 `data/wechat/auto_exports/`

系统会在几分钟内自动处理并生成推荐！

---

## 🎯 详细步骤

### 第1步：准备环境

```bash
# 进入项目目录
cd ~/chattingclaire

# 安装依赖（只需要一次）
pip install -r requirements.txt

# 启动自动收集器（后台运行）
nohup ./start_auto_collector.sh > logs/collector.log 2>&1 &
```

### 第2步：每天导出消息

**方式A：使用格式化工具（推荐）**

```bash
# 1. Mac微信复制消息

# 2. 运行工具
python tools/format_wechat_paste.py

# 3. 粘贴内容
# (工具会自动格式化并保存)
```

**方式B：手动格式化**

```bash
# 1. 创建文件
vim ~/Desktop/180k_today.txt

# 2. 粘贴并整理成这个格式：
# [2025-01-17 10:30:00] 张三: 贵州茅台今天涨停了
# [2025-01-17 10:35:00] 李四: 600519目标价2800

# 3. 保存并复制到监控目录
cp ~/Desktop/180k_today.txt ~/chattingclaire/data/wechat/auto_exports/
```

### 第3步：查看结果

```bash
# 等待5-10分钟后，查看推荐
python -c "
from database.supabase_client import get_supabase_client
from datetime import date

db = get_supabase_client()
picks = db.table('stock_picks')\
    .select('*')\
    .gte('created_at', f'{date.today()}T00:00:00')\
    .limit(10)\
    .execute()

print(f'今天生成了 {len(picks.data)} 个推荐\n')

for p in picks.data:
    print(f\"{p['ticker']}: {p['action']} - 置信度 {p['confidence']:.1%}\")
"
```

---

## 💡 实用技巧

### 技巧1：创建快捷命令

编辑 `~/.zshrc`（或 `~/.bash_profile`）：

```bash
# 添加这些别名
alias wechat-format="cd ~/chattingclaire && python tools/format_wechat_paste.py"
alias wechat-check="python -c 'from database.supabase_client import get_supabase_client; from datetime import date; db = get_supabase_client(); picks = db.table(\"stock_picks\").select(\"*\").gte(\"created_at\", f\"{date.today()}T00:00:00\").execute(); print(f\"今天 {len(picks.data)} 个推荐\"); [print(f\"{p[\"ticker\"]}: {p[\"action\"]}\") for p in picks.data[:5]]'"

# 保存后
source ~/.zshrc
```

现在可以这样用：

```bash
# 格式化微信内容
wechat-format

# 查看今天的推荐
wechat-check
```

### 技巧2：Mac自动化（Automator）

创建一个快速操作：

1. 打开 **Automator**
2. 新建 **快速操作**
3. 添加动作：**运行Shell脚本**
4. 粘贴：
   ```bash
   cd ~/chattingclaire
   python tools/format_wechat_paste.py
   ```
5. 保存为 **"格式化微信消息"**

现在：
- 右键点击 → 服务 → 格式化微信消息

### 技巧3：每日提醒

在Mac **提醒事项** 中设置：

```
每天 23:00
提醒：导出"180K - 星球讨论群🪙"今日消息
```

---

## 🎬 完整每日工作流

### 早上（开盘前）

```bash
# 检查自动收集器是否运行
ps aux | grep auto_collector

# 如果没运行，启动它
cd ~/chattingclaire
nohup ./start_auto_collector.sh > logs/collector.log 2>&1 &
```

### 晚上（收盘后）

```bash
# 1. 打开Mac微信
# 2. 进入"180K - 星球讨论群🪙"
# 3. Cmd+A 全选 → Cmd+C 复制

# 4. 格式化并保存
cd ~/chattingclaire
python tools/format_wechat_paste.py
# 粘贴 → Ctrl+D → 输入 y 保存

# 5. 等5-10分钟，查看结果
python -c "
from database.supabase_client import get_supabase_client
from datetime import date
db = get_supabase_client()
picks = db.table('stock_picks').select('*').gte('created_at', f'{date.today()}T00:00:00').execute()
for p in picks.data[:5]:
    print(f'{p[\"ticker\"]}: {p[\"action\"]} ({p[\"confidence\"]:.1%})')
"
```

---

## 🖼️ 如果群里有图片和PDF

Mac上处理图片和PDF：

### 方法1：用WechatExporter

```bash
# 安装
brew install --cask wechat-exporter

# 运行并导出群聊
# 选择导出图片和附件
```

详细教程：`docs/MAC_WECHAT_EXPORT.md`

### 方法2：手动保存图片

1. Mac微信中右键图片 → "另存为"
2. 保存到 `~/chattingclaire/data/wechat/images/`
3. 系统会自动OCR识别

---

## ❓ 常见问题

### Q: 复制的内容格式不对怎么办？

**A**: 用格式化工具会自动处理：
```bash
python tools/format_wechat_paste.py
```

### Q: 能批量导出历史数据吗？

**A**: 可以，用WechatExporter：
```bash
brew install --cask wechat-exporter
# 导出后用转换工具处理
```

### Q: 需要每天手动导出吗？

**A**: 是的，个人微信暂时没有更好的自动化方案。
但只需要：复制 → 运行工具 → 完成，很快的！

### Q: 可以在手机上导出吗？

**A**: 可以通过iCloud：
1. iPhone微信 → 选择消息 → 分享到iCloud备忘录
2. Mac打开备忘录 → 复制内容
3. 运行格式化工具

---

## 🚀 一键开始

```bash
# 完整设置（只需一次）
cd ~
git clone <your-repo>  # 如果还没clone
cd chattingclaire
pip install -r requirements.txt

# 启动自动收集器
./start_auto_collector.sh &

# 现在每天只需要：
# 1. Mac微信复制消息
# 2. 运行：python tools/format_wechat_paste.py
# 3. 粘贴 → 保存
# 完成！
```

---

## 📊 工作流对比

| 步骤 | Windows | Mac |
|------|---------|-----|
| 导出工具 | WeChatMsg.exe | 手动复制 |
| 格式化 | 自动 | format_wechat_paste.py |
| 难度 | ⭐⭐ | ⭐ |
| 速度 | 5分钟 | 3分钟 |

**Mac反而更简单！**

---

## 📚 相关文档

- **Mac详细导出**: `docs/MAC_WECHAT_EXPORT.md`
- **通用指南**: `QUICK_START_180K.md`
- **图片PDF处理**: `IMAGE_PDF_QUICKSTART.md`

---

## ✨ 总结

**Mac最简单的方法**：

```bash
# 1. 复制
Mac微信 → Cmd+C

# 2. 格式化
python tools/format_wechat_paste.py
# 粘贴 → Ctrl+D → y

# 3. 完成！
```

**只需要3步，不到3分钟！**

开始使用吧！🚀
