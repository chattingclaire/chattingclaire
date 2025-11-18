# 个人微信导出 - 3分钟上手

最快最简单的个人微信消息导出方法。

---

## 🚀 方法1：复制粘贴（最快）

### 1️⃣ 在PC微信复制消息

<img src="https://via.placeholder.com/600x300?text=PC%E5%BE%AE%E4%BF%A1%E7%95%8C%E9%9D%A2" alt="PC微信" width="600"/>

1. 打开PC微信
2. 进入股票群聊
3. 选中想要的消息（按住Ctrl点击）
4. 右键 → 复制

### 2️⃣ 创建文本文件

创建 `my_wechat.txt`，粘贴并整理成这个格式：

```
[2025-01-15 10:30:00] 张三: 贵州茅台今天涨停了
[2025-01-15 10:35:00] 李四: 600519目标价2800
[2025-01-15 11:00:00] 王五: 看好白酒板块
```

**格式**：`[时间] 昵称: 内容`

### 3️⃣ 放到监控目录

```bash
cp my_wechat.txt data/wechat/auto_exports/
```

✅ **完成！系统会自动处理**

---

## 📦 方法2：用工具批量导出（推荐）

### Windows用户

1. **下载WeChatMsg**
   ```
   https://github.com/LC044/WeChatMsg/releases
   ```
   下载最新的 `WeChatMsg.exe`

2. **运行程序**
   - 双击运行
   - 会自动读取微信数据

3. **选择群聊**
   - 左侧选择要导出的群聊
   - 可以多选

4. **导出**
   - 格式选择：**JSON**
   - 保存位置：`chattingclaire/data/wechat/exports/`
   - 点击"导出"

5. **移动到监控目录**
   ```bash
   cp data/wechat/exports/*.json data/wechat/auto_exports/
   ```

✅ **完成！**

### Mac用户

```bash
# 1. 安装WeChatMsg
git clone https://github.com/LC044/WeChatMsg.git
cd WeChatMsg
pip3 install -r requirements.txt

# 2. 运行
python3 main.py

# 3. 在界面中选择群聊并导出为JSON

# 4. 移动文件
cp ~/导出的文件.json ~/chattingclaire/data/wechat/auto_exports/
```

---

## 🎯 完整示例

假设你今天在群里看到了这些消息：

**原始消息**（PC微信）：
```
张三 10:30
贵州茅台今天涨停了，基本面持续向好

李四 10:35
600519目标价2800，白酒板块整体走强

王五 11:00
茅台Q4业绩超预期，建议关注
```

**格式化为**（my_wechat.txt）：
```
[2025-01-15 10:30:00] 张三: 贵州茅台今天涨停了，基本面持续向好
[2025-01-15 10:35:00] 李四: 600519目标价2800，白酒板块整体走强
[2025-01-15 11:00:00] 王五: 茅台Q4业绩超预期，建议关注
```

**或者用JSON**（my_wechat.json）：
```json
[
  {
    "sender": "张三",
    "content": "贵州茅台今天涨停了，基本面持续向好",
    "timestamp": "2025-01-15T10:30:00"
  },
  {
    "sender": "李四",
    "content": "600519目标价2800，白酒板块整体走强",
    "timestamp": "2025-01-15T10:35:00"
  },
  {
    "sender": "王五",
    "content": "茅台Q4业绩超预期，建议关注",
    "timestamp": "2025-01-15T11:00:00"
  }
]
```

**然后**：
```bash
cp my_wechat.txt data/wechat/auto_exports/
# 或
cp my_wechat.json data/wechat/auto_exports/
```

---

## ⚡ 每日工作流

### 早上9:30（开盘前）

```bash
# 1. 启动自动收集器（如果还没启动）
./start_auto_collector.sh &

# 现在它会每5分钟检查一次新文件
```

### 晚上收盘后

```bash
# 1. 打开PC微信，进入股票群
# 2. 复制今天的讨论内容
# 3. 粘贴到 today.txt 并整理格式
# 4. 保存并复制

cp today.txt data/wechat/auto_exports/

# 5. 等几分钟，系统自动处理
# 6. 查看推荐

python -c "
from database.supabase_client import get_supabase_client
db = get_supabase_client()
picks = db.table('stock_picks').select('*').limit(10).execute()
for p in picks.data:
    print(f\"{p['ticker']}: {p['action']}\")
"
```

---

## 📝 最简格式

**最少只需要2个字段**：

```json
[
  {"content": "贵州茅台涨停", "sender": "张三"},
  {"content": "600519目标价2800", "sender": "李四"}
]
```

或者TXT：
```
张三: 贵州茅台涨停
李四: 600519目标价2800
```

**系统会自动补充时间戳！**

---

## 🔧 常用命令

```bash
# 查看监控目录
ls -lh data/wechat/auto_exports/

# 查看已处理文件
cat data/wechat/auto_exports/.processed_files.txt

# 手动处理单个文件
python -c "
from agents.wx_source.agent import WxSourceAgent
agent = WxSourceAgent()
result = agent.run('my_wechat.txt')
print(f'处理了 {result[\"processed_messages\"]} 条消息')
"

# 查看今天的消息数
python -c "
from database.supabase_client import get_supabase_client
from datetime import date
db = get_supabase_client()
count = db.table('wx_raw_messages').select('*', count='exact').gte('created_at', f'{date.today()}T00:00:00').execute()
print(f'今天收集了 {count.count} 条消息')
"
```

---

## ❓ FAQ

**Q: 必须要时间戳吗？**
A: 不是必须的，系统会自动生成

**Q: 支持什么格式？**
A: JSON, TXT, CSV 都可以

**Q: 可以手机导出吗？**
A: 可以，在手机上复制消息，发邮件给自己，然后在电脑上整理

**Q: 时间写错了怎么办？**
A: 没关系，只要格式对就行，时间不影响分析

**Q: 一次能处理多少条消息？**
A: 建议单个文件不超过1000条，太多的话拆分成多个文件

---

## 🎯 推荐工具

**Windows**:
- WeChatMsg (https://github.com/LC044/WeChatMsg)
- Notepad++ (编辑文本)

**Mac**:
- WeChatMsg (需要Python)
- VSCode (编辑文本)

**在线工具**:
- JSON格式化：https://jsonformatter.org/
- CSV编辑器：Excel, Google Sheets

---

## 📚 下一步

- **详细教程**：查看 `docs/WECHAT_MANUAL_EXPORT.md`
- **自动化**：查看 `AUTO_COLLECTION_QUICKSTART.md`
- **格式参考**：查看 `WECHAT_QUICKREF.md`

---

## ✨ 最简单的开始

```bash
# 1. 创建测试文件
cat > test.txt << 'EOF'
[2025-01-15 10:30:00] 张三: 贵州茅台600519涨停
[2025-01-15 10:35:00] 李四: 宁德时代300750也不错
EOF

# 2. 复制到监控目录
cp test.txt data/wechat/auto_exports/

# 3. 启动收集器
./start_auto_collector.sh --once

# 4. 查看结果
# 如果成功，test.txt 会被处理并记录
```

就这么简单！🚀
