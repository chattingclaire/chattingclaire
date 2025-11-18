# 个人微信消息手动导出指南

如何从个人微信（非企业微信）导出群聊消息到系统中。

---

## 🚀 方法1：复制粘贴（最简单，5分钟）

### 适合场景
- 快速测试
- 少量消息（10-50条）
- 不需要历史数据

### 操作步骤

#### Step 1: 在PC微信复制消息

1. 打开PC端微信
2. 进入要导出的群聊
3. 滚动到你想要的消息位置
4. 按住 `Ctrl` (Windows) 或 `Cmd` (Mac)，点击选择多条消息
5. 右键 → "复制"

#### Step 2: 粘贴到文本文件

创建文件 `my_wechat.txt`，粘贴内容，格式化为：

```text
[2025-01-15 10:30:00] 张三: 贵州茅台今天涨停了
[2025-01-15 10:35:00] 李四: 600519目标价2800
[2025-01-15 11:00:00] 王五: 茅台业绩超预期
```

**格式要求**：
- 每行一条消息
- 格式：`[时间] 昵称: 内容`
- 时间格式：`YYYY-MM-DD HH:MM:SS`

#### Step 3: 导入系统

```bash
# 放到监控目录
cp my_wechat.txt data/wechat/auto_exports/

# 或者直接处理
python -c "
from agents.wx_source.agent import WxSourceAgent
agent = WxSourceAgent()
results = agent.run('my_wechat.txt')
print(f'处理了 {results[\"processed_messages\"]} 条消息')
"
```

---

## 📦 方法2：使用WeChatMsg（推荐，完整导出）

### 适合场景
- 导出完整聊天记录
- 批量导出多个群聊
- 需要历史数据
- 一次性导出大量消息

### 安装WeChatMsg

#### Windows

```bash
# 1. 下载WeChatMsg
git clone https://github.com/LC044/WeChatMsg.git
cd WeChatMsg

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python main.py
```

或者直接下载exe：
- 访问：https://github.com/LC044/WeChatMsg/releases
- 下载最新版本的 `WeChatMsg.exe`
- 双击运行

#### Mac

```bash
# 1. 下载
git clone https://github.com/LC044/WeChatMsg.git
cd WeChatMsg

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 运行
python3 main.py
```

### 使用WeChatMsg导出

1. **启动WeChatMsg**
   - 运行后会自动检测微信数据库

2. **选择联系人/群聊**
   - 左侧列表选择要导出的群聊
   - 可以多选

3. **选择导出格式**
   - 推荐选择：**JSON格式**
   - 也支持：HTML, TXT, CSV

4. **导出**
   - 点击"导出"按钮
   - 选择保存位置（建议：`chattingclaire/data/wechat/exports/`）
   - 等待导出完成

5. **导入系统**
   ```bash
   # 假设导出到了 ~/Downloads/wechat_export.json
   cp ~/Downloads/wechat_export.json data/wechat/auto_exports/

   # 系统会自动处理（如果启动了auto_collector）
   # 或者手动处理：
   python examples/wechat_input_example.py
   ```

### WeChatMsg导出格式示例

导出的JSON格式：
```json
[
  {
    "id": 1,
    "from_user": "张三",
    "message": "贵州茅台今天涨停了",
    "time": "2025-01-15 10:30:00",
    "type": 1
  },
  {
    "id": 2,
    "from_user": "李四",
    "message": "600519目标价2800",
    "time": "2025-01-15 10:35:00",
    "type": 1
  }
]
```

**系统会自动识别并标准化这种格式！**

---

## 🖥️ 方法3：PC微信聊天记录直接导出

### Windows PC微信

1. **打开聊天窗口**
   - 打开要导出的群聊

2. **选择消息**
   - 右上角 → 设置 → "聊天记录备份与迁移"
   - 或者：选中消息 → 右键 → "合并转发"

3. **导出为文件**
   - 转发给"文件传输助手"
   - 在文件传输助手中查看
   - 复制内容到文本文件

### Mac微信

1. **选择消息**
   - 在群聊中选择要导出的消息
   - `Cmd + C` 复制

2. **格式化**
   - 粘贴到文本编辑器
   - 整理成标准格式

---

## 🎯 方法4：手机端导出

### iPhone

1. **选择消息**
   - 长按消息 → "多选"
   - 选择要导出的消息

2. **导出**
   - 点击左下角分享图标
   - 选择"邮件"或"备忘录"
   - 发送给自己

3. **整理格式**
   - 在电脑上打开邮件/备忘录
   - 复制内容
   - 整理成标准格式保存

### Android

1. **备份聊天记录**
   - 群聊设置 → 聊天记录备份
   - 通过邮件发送给自己

2. **整理**
   - 在电脑上打开邮件
   - 复制内容并格式化

---

## 📝 方法5：手动创建文件（最灵活）

### 适合场景
- 只有几条重要消息
- 想要自定义格式
- 测试系统功能

### JSON格式（推荐）

创建 `my_messages.json`：

```json
[
  {
    "sender": "张三",
    "content": "贵州茅台今天涨停了，基本面持续向好",
    "timestamp": "2025-01-15T10:30:00",
    "chat_name": "股票交流群"
  },
  {
    "sender": "李四",
    "content": "600519目标价2800，白酒板块整体走强",
    "timestamp": "2025-01-15T10:35:00",
    "chat_name": "股票交流群"
  },
  {
    "sender": "王五",
    "content": "茅台Q4业绩超预期，营收同比增长15%",
    "timestamp": "2025-01-15T11:00:00",
    "chat_name": "股票交流群"
  }
]
```

### TXT格式（最简单）

创建 `my_messages.txt`：

```text
[2025-01-15 10:30:00] 张三: 贵州茅台今天涨停了，基本面持续向好
[2025-01-15 10:35:00] 李四: 600519目标价2800，白酒板块整体走强
[2025-01-15 11:00:00] 王五: 茅台Q4业绩超预期，营收同比增长15%
```

### CSV格式

创建 `my_messages.csv`：

```csv
sender,content,timestamp,chat_name
张三,贵州茅台今天涨停了，2025-01-15T10:30:00,股票交流群
李四,600519目标价2800,2025-01-15T10:35:00,股票交流群
王五,茅台Q4业绩超预期,2025-01-15T11:00:00,股票交流群
```

---

## 🔄 完整工作流示例

### 每日使用流程

```bash
# ===== 早上 =====
# 1. 打开PC微信，查看股票群聊

# 2. 复制今天的讨论内容
# Ctrl+A 全选今天的消息 → Ctrl+C 复制

# 3. 粘贴并格式化
vim today_messages.txt
# 粘贴并整理格式

# 4. 导入系统
cp today_messages.txt data/wechat/auto_exports/

# ===== 系统自动处理 =====
# 如果启动了auto_collector，会自动：
# - 检测新文件
# - 解析消息
# - 提取股票信号
# - 生成推荐

# ===== 查看结果 =====
# 查看今天的推荐
python -c "
from database.supabase_client import get_supabase_client
from datetime import date

db = get_supabase_client()
today = date.today().isoformat()

picks = db.table('stock_picks')\
    .select('*')\
    .gte('created_at', f'{today}T00:00:00')\
    .execute()

for pick in picks.data:
    print(f\"{pick['ticker']}: {pick['action']} - 置信度 {pick['confidence']:.1%}\")
"
```

---

## 💡 实用技巧

### 技巧1：快速测试

如果只想快速测试，创建一个简单的文件：

```bash
cat > test.txt << 'EOF'
[2025-01-15 10:30:00] 测试用户: 贵州茅台600519涨停
[2025-01-15 10:35:00] 测试用户: 宁德时代300750也不错
EOF

# 测试处理
python examples/wechat_input_example.py
```

### 技巧2：批量导出多个群

```bash
# 使用WeChatMsg批量导出
# 1. 选中所有股票相关的群聊
# 2. 导出为JSON到同一个目录
# 3. 系统会自动处理目录中的所有文件

cp -r ~/Downloads/wechat_exports/* data/wechat/auto_exports/
```

### 技巧3：定期导出

**Windows任务计划**：
```
任务：每天晚上23:00提醒导出微信消息
操作：弹出提醒
```

**Mac提醒事项**：
```
每天23:00：导出微信群聊消息
```

### 技巧4：消息预处理

如果导出的格式不标准，可以用脚本转换：

```python
# convert_wechat.py
"""转换微信导出格式"""

import re
from datetime import datetime

# 读取原始文件
with open('raw_messages.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 转换格式
output = []
for line in lines:
    # 假设原始格式：2025-01-15 10:30 张三：消息内容
    match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+(.+?)[:：]\s*(.+)', line.strip())
    if match:
        time_str, sender, content = match.groups()
        # 转换为标准格式
        formatted = f"[{time_str}:00] {sender}: {content}"
        output.append(formatted)

# 保存
with open('formatted_messages.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"转换了 {len(output)} 条消息")
```

---

## 📊 对比表格

| 方法 | 难度 | 速度 | 数据量 | 推荐度 |
|-----|------|------|--------|--------|
| 复制粘贴 | ⭐ | 快 | 少量 | ⭐⭐⭐ 测试用 |
| WeChatMsg | ⭐⭐ | 中 | 大量 | ⭐⭐⭐⭐⭐ 推荐 |
| PC导出 | ⭐⭐ | 中 | 中量 | ⭐⭐⭐⭐ |
| 手机导出 | ⭐⭐⭐ | 慢 | 少量 | ⭐⭐ 备用 |
| 手动创建 | ⭐ | 快 | 极少 | ⭐⭐⭐ 测试 |

---

## ⚠️ 注意事项

### 1. 时间格式
确保时间格式正确：
- ✅ `2025-01-15 10:30:00`
- ✅ `2025-01-15T10:30:00`
- ❌ `15/01/2025 10:30` (不支持)

### 2. 编码问题
- 使用 **UTF-8** 编码保存文件
- Windows记事本可能有问题，建议用 Notepad++ 或 VSCode

### 3. 特殊字符
- 避免在内容中使用未配对的引号
- 如果有JSON格式，确保转义特殊字符

### 4. 文件大小
- 单个文件建议不超过1000条消息
- 太大的文件拆分成多个

---

## 🎯 推荐方案

### 个人使用（推荐）
```
1. 每天用PC微信复制粘贴当天消息 → TXT格式
2. 每周用WeChatMsg导出一次完整记录 → JSON格式
3. 放到监控目录，自动处理
```

### 团队使用
```
1. 每人导出各自关注的群 → JSON格式
2. 统一放到共享目录
3. 系统批量处理
```

---

## 📚 相关文档

- **自动收集器**：`AUTO_COLLECTION_QUICKSTART.md` - 设置自动处理
- **格式参考**：`WECHAT_QUICKREF.md` - 支持的格式
- **完整教程**：`docs/WECHAT_USAGE.md` - 详细使用指南

---

## 🚀 快速开始

```bash
# 1. 复制消息到文件
vim my_wechat.txt
# 粘贴格式：[2025-01-15 10:30:00] 张三: 贵州茅台涨停

# 2. 启动自动收集器
./start_auto_collector.sh

# 3. 放入文件
cp my_wechat.txt data/wechat/auto_exports/

# 4. 完成！系统自动处理
```

就这么简单！🎉
