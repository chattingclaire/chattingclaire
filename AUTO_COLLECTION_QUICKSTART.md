# 微信自动接收 - 快速开始

最简单的方式实现微信消息自动接收和处理。

---

## 🚀 最快上手（3步）

### 1️⃣ 启动自动收集器

```bash
./start_auto_collector.sh
```

### 2️⃣ 把微信导出文件放到监控目录

```bash
# 复制你的微信导出文件
cp my_wechat_messages.json data/wechat/auto_exports/

# 系统会自动检测并处理！
```

### 3️⃣ 完成！✅

系统会：
- ✅ 自动检测新文件
- ✅ 自动解析消息
- ✅ 自动索引到数据库
- ✅ 自动提取股票信号

---

## 📁 工作原理

```
你导出微信消息
      ↓
放到监控目录 (data/wechat/auto_exports/)
      ↓
自动收集器每5分钟扫描一次
      ↓
自动解析 → 自动索引 → 自动分析
      ↓
生成股票推荐！
```

---

## ⚙️ 配置选项

### 基础配置（必需）

```bash
# 编辑 .env 文件
WECHAT_WATCH_DIR=data/wechat/auto_exports  # 监控目录
```

### 高级配置（可选）

#### 选项1：添加公众号RSS

```bash
# .env 文件中添加
WECHAT_RSS_FEEDS=https://werss.app/feed/xxx,https://werss.app/feed/yyy

# 获取RSS链接：
# 1. 访问 https://werss.app/
# 2. 订阅你关注的公众号
# 3. 复制RSS链接
```

#### 选项2：启用企业微信

```bash
# .env 文件中添加
WECOM_CORP_ID=ww1234567890abcdef
WECOM_AGENT_ID=1000001
WECOM_SECRET=your_secret_here

# 获取方式：
# 1. 注册企业微信：https://work.weixin.qq.com/
# 2. 创建自建应用
# 3. 获取配置参数
```

#### 选项3：自动运行Pipeline

```bash
# .env 文件中添加
AUTO_RUN_PIPELINE=true

# true = 检测到新消息后自动生成股票推荐
# false = 只收集消息，不自动分析
```

---

## 🎯 使用场景

### 场景1：每天手动导出（最简单）

**适合**：小规模使用、测试阶段

```bash
# 1. 启动收集器（后台运行）
nohup ./start_auto_collector.sh &

# 2. 每天导出微信消息（手动）
# 在手机/PC上导出群聊为JSON

# 3. 复制到监控目录
cp ~/Downloads/wechat_export.json data/wechat/auto_exports/

# 4. 系统自动处理！
```

### 场景2：RSS订阅公众号（自动）

**适合**：关注特定公众号、中长期策略

```bash
# 1. 配置RSS订阅（一次性）
echo "WECHAT_RSS_FEEDS=https://werss.app/feed/xxx" >> .env

# 2. 启动收集器
./start_auto_collector.sh

# 3. 系统自动拉取公众号文章！
```

### 场景3：企业微信（全自动）

**适合**：团队使用、生产环境

```bash
# 1. 配置企业微信（一次性）
echo "WECOM_CORP_ID=xxx" >> .env
echo "WECOM_AGENT_ID=xxx" >> .env
echo "WECOM_SECRET=xxx" >> .env

# 2. 启动收集器
./start_auto_collector.sh

# 3. 在企业微信群聊天即可，系统实时接收！
```

### 场景4：混合模式（推荐）

**适合**：完整方案

```bash
# 同时使用：
# - 手动导出个人微信（每天1-2次）
# - RSS订阅公众号（自动）
# - 企业微信群聊（实时）

# 一次性配置
cat >> .env << EOF
WECHAT_WATCH_DIR=data/wechat/auto_exports
WECHAT_RSS_FEEDS=https://werss.app/feed/xxx
WECOM_CORP_ID=xxx
WECOM_AGENT_ID=xxx
WECOM_SECRET=xxx
AUTO_RUN_PIPELINE=true
EOF

# 启动
./start_auto_collector.sh

# 然后就全自动了！
```

---

## 🔧 命令选项

### 默认运行（5分钟间隔）

```bash
./start_auto_collector.sh
```

### 自定义间隔

```bash
# 每1分钟检查一次
./start_auto_collector.sh --interval 60

# 每30分钟检查一次
./start_auto_collector.sh --interval 1800
```

### 只运行一次

```bash
# 处理当前目录下的所有新文件，然后退出
./start_auto_collector.sh --once
```

### 后台运行

```bash
# 使用nohup后台运行
nohup ./start_auto_collector.sh > logs/auto_collector.log 2>&1 &

# 查看进程
ps aux | grep auto_collector

# 查看日志
tail -f logs/auto_collector.log

# 停止
pkill -f auto_collector
```

---

## 📊 监控和管理

### 查看收集统计

```python
# 查看今天收集的消息数
from database.supabase_client import get_supabase_client
from datetime import date

db = get_supabase_client()
today = date.today().isoformat()

count = db.table("wx_raw_messages")\
    .select("*", count="exact")\
    .gte("created_at", f"{today}T00:00:00")\
    .execute()

print(f"今天收集了 {count.count} 条消息")
```

### 查看已处理文件

```bash
# 查看已处理文件列表
cat data/wechat/auto_exports/.processed_files.txt

# 文件数量
wc -l data/wechat/auto_exports/.processed_files.txt
```

### 重新处理文件

```bash
# 删除处理记录
rm data/wechat/auto_exports/.processed_files.txt

# 下次运行会重新处理所有文件
./start_auto_collector.sh --once
```

---

## 💡 实用技巧

### 技巧1：定时任务自动运行

```bash
# Linux/Mac - 使用crontab
crontab -e

# 添加：每小时运行一次
0 * * * * cd /path/to/chattingclaire && ./start_auto_collector.sh --once

# 或者：系统启动时运行
@reboot cd /path/to/chattingclaire && nohup ./start_auto_collector.sh &
```

### 技巧2：Telegram/Discord通知

```python
# 在 tools/auto_collector.py 的 run_collection_cycle() 末尾添加

if total > 0:
    # 发送Telegram通知
    import requests
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if bot_token and chat_id:
        message = f"📊 收集了 {total} 条新消息"
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message}
        )
```

### 技巧3：批量导出历史数据

```bash
# 创建脚本批量处理历史文件
mkdir -p data/wechat/history

# 将所有历史导出文件放到history目录
# 然后一次性处理

WECHAT_WATCH_DIR=data/wechat/history ./start_auto_collector.sh --once
```

---

## ❓ 常见问题

### Q: 支持哪些文件格式？

**A**: JSON, CSV, TXT - 会自动检测格式

### Q: 文件会重复处理吗？

**A**: 不会，已处理的文件会记录在 `.processed_files.txt`

### Q: 如何确认系统正在运行？

**A**:
```bash
# 查看进程
ps aux | grep auto_collector

# 查看日志
tail -f logs/auto_collector.log
```

### Q: 如何停止自动收集器？

**A**:
```bash
# 找到进程ID
ps aux | grep auto_collector

# 停止进程
kill <PID>

# 或者
pkill -f auto_collector
```

### Q: 可以同时监控多个目录吗？

**A**: 可以运行多个实例，分别监控不同目录：
```bash
WECHAT_WATCH_DIR=data/wechat/group1 ./start_auto_collector.sh &
WECHAT_WATCH_DIR=data/wechat/group2 ./start_auto_collector.sh &
```

---

## 📚 相关文档

- **详细教程**: `docs/WECHAT_AUTO_COLLECTION.md`
- **手动导入**: `docs/WECHAT_USAGE.md`
- **快速参考**: `WECHAT_QUICKREF.md`

---

## ✨ 总结

**最简单用法**：
```bash
# 1. 启动
./start_auto_collector.sh

# 2. 放文件
cp my_messages.json data/wechat/auto_exports/

# 3. 完成！
```

**完整自动化**：
```bash
# 配置RSS和企业微信
vim .env

# 启动后台运行
nohup ./start_auto_collector.sh &

# 然后就全自动了！
```

就这么简单！🚀
