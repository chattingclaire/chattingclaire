# "180K - 星球讨论群🪙" 快速使用指南

专门为你的星球讨论群配置的快速指南。

---

## ✅ 已完成配置

系统现在会**只监控**这个群："180K - 星球讨论群🪙"

**配置详情**：
- 精确群名匹配：`180K - 星球讨论群🪙`
- 关键词匹配：包含"星球"或"讨论"的群也会被监控
- 内容过滤：处理所有消息（不过滤）
- 排除广告：自动过滤包含"广告"、"推广"的消息

**配置文件**：`config/monitored_sources.yaml`

---

## 🚀 开始使用（3步）

### 方法A：手动复制粘贴（最快）

#### 1. 从PC微信复制消息

1. 打开PC微信
2. 进入"180K - 星球讨论群🪙"
3. 选择今天的消息（按住Ctrl点击多条）
4. 右键 → 复制

#### 2. 创建文件并格式化

创建 `180k_today.txt`：

```
[2025-01-17 10:30:00] 张三: 贵州茅台今天涨停了，基本面持续向好
[2025-01-17 10:35:00] 李四: 600519目标价2800，白酒板块整体走强
[2025-01-17 11:00:00] 王五: 茅台Q4业绩超预期，建议关注
```

**格式**：`[时间] 昵称: 消息内容`

#### 3. 导入系统

```bash
# 复制到监控目录
cp 180k_today.txt data/wechat/auto_exports/

# 或者手动处理
python -c "
from agents.wx_source.agent import WxSourceAgent
agent = WxSourceAgent()
results = agent.run('180k_today.txt')
print(f'处理了 {results[\"processed_messages\"]} 条消息')
"
```

---

### 方法B：用WeChatMsg批量导出（推荐）

#### 1. 下载并运行WeChatMsg

**Windows**:
```
下载: https://github.com/LC044/WeChatMsg/releases
运行: WeChatMsg.exe
```

**Mac**:
```bash
git clone https://github.com/LC044/WeChatMsg.git
cd WeChatMsg
pip install -r requirements.txt
python main.py
```

#### 2. 导出群聊

1. 在WeChatMsg中找到"180K - 星球讨论群🪙"
2. ✅ 勾选"导出图片"（如果群里有K线图、截图）
3. ✅ 勾选"导出附件"（如果有PDF研报）
4. 选择格式：**JSON**
5. 保存位置：`chattingclaire/data/wechat/exports/180k_group`
6. 点击"导出"

#### 3. 导入系统

```bash
# 复制导出目录
cp -r data/wechat/exports/180k_group data/wechat/auto_exports/

# 系统会自动：
# - 解析所有消息
# - OCR识别图片中的股票代码
# - 提取PDF研报内容
# - 索引到数据库
```

---

### 方法C：自动化收集（后台运行）

#### 1. 启动自动收集器

```bash
# 后台运行，每5分钟检查一次新文件
nohup ./start_auto_collector.sh > logs/collector.log 2>&1 &

# 查看日志
tail -f logs/collector.log
```

#### 2. 每天导出放到监控目录

```bash
# 创建今天的导出文件
vim data/wechat/auto_exports/180k_$(date +%Y%m%d).txt

# 粘贴并格式化消息
# 保存后系统会自动处理
```

---

## 🖼️ 处理图片和PDF

如果群里经常发K线图、财报截图、研报PDF：

### 1. 安装OCR和PDF工具

```bash
pip install paddleocr pdfplumber
```

### 2. 用WeChatMsg导出时勾选图片和附件

这样导出的数据会包含：
```
180k_group/
├── messages.json          # 消息
├── images/                # 所有图片
│   ├── kline_001.jpg     # K线图
│   ├── report_002.png    # 财报截图
│   └── ...
└── files/                 # 所有附件
    ├── research.pdf      # 研报
    └── ...
```

### 3. 系统自动处理

```bash
cp -r 180k_group data/wechat/auto_exports/

# 系统会：
# 1. OCR识别图片文字（股票代码、价格、技术指标）
# 2. 提取PDF内容（研报摘要、评级、目标价）
# 3. 全部索引到向量数据库
```

---

## 📊 查看结果

### 查询收集的消息

```python
from memory.enhanced_context import get_enhanced_context_manager

ctx = get_enhanced_context_manager()

# 搜索星球群里的讨论
results = ctx.search_similar_content(
    query="贵州茅台",
    source_filter="wx_raw_messages",
    limit=10
)

for r in results:
    print(f"相似度: {r['similarity_score']:.2f}")
    print(f"内容: {r['content'][:100]}")
    print()
```

### 查看生成的股票推荐

```python
from database.supabase_client import get_supabase_client
from datetime import date

db = get_supabase_client()
today = date.today().isoformat()

# 查询今天的推荐
picks = db.table('stock_picks')\
    .select('*')\
    .gte('created_at', f'{today}T00:00:00')\
    .order('confidence', desc=True)\
    .limit(10)\
    .execute()

print(f"今天的推荐 ({len(picks.data)} 只):\n")

for pick in picks.data:
    print(f"{pick['ticker']}: {pick['action']}")
    print(f"  置信度: {pick['confidence']:.1%}")
    print(f"  微信权重: {pick['wx_weight']:.1%}")
    print(f"  目标价: ¥{pick.get('target_price', 'N/A')}")
    print(f"  原因: {', '.join(pick['reasons'][:2])}")
    print()
```

---

## 🔍 验证配置

```bash
# 测试过滤器配置
python test_filter.py

# 应该显示：
# ✓ 监控 - 180K - 星球讨论群🪙
# ✗ 忽略 - 家人群
# ✗ 忽略 - 同学群
```

---

## 📝 每日工作流建议

### 早上开盘前

```bash
# 1. 启动自动收集器（如果还没启动）
./start_auto_collector.sh &
```

### 晚上收盘后

```bash
# 1. 打开PC微信，进入"180K - 星球讨论群🪙"
# 2. 复制今天的讨论内容
# 3. 粘贴到文件并整理格式

vim 180k_today.txt
# 粘贴并整理为：
# [时间] 昵称: 内容

# 4. 导入
cp 180k_today.txt data/wechat/auto_exports/

# 5. 等几分钟，查看结果
python -c "
from database.supabase_client import get_supabase_client
from datetime import date
db = get_supabase_client()
picks = db.table('stock_picks').select('*').gte('created_at', f'{date.today()}T00:00:00').execute()
print(f'今天生成了 {len(picks.data)} 个推荐')
for p in picks.data[:5]:
    print(f'  {p[\"ticker\"]}: {p[\"action\"]} (置信度 {p[\"confidence\"]:.1%})')
"
```

---

## 🎯 示例：完整流程

假设今天在星球群里看到这些讨论：

**原始消息**：
```
张三 14:30
贵州茅台今天放量上涨，突破前期高点

李四 14:35
600519技术面很强，建议继续持有

王五 15:00
[图片：K线图.jpg]  # 显示茅台日线突破
```

**整理为TXT**：
```
[2025-01-17 14:30:00] 张三: 贵州茅台今天放量上涨，突破前期高点
[2025-01-17 14:35:00] 李四: 600519技术面很强，建议继续持有
[2025-01-17 15:00:00] 王五: [图片：K线图]
```

**或用WeChatMsg导出（推荐）**：
- 自动包含图片
- 系统会OCR识别图片内容

**导入并查看结果**：
```bash
cp 180k_20250117.txt data/wechat/auto_exports/

# 等待处理（5-10分钟）

# 查看推荐
python -c "
from database.supabase_client import get_supabase_client
db = get_supabase_client()
picks = db.table('stock_picks').select('*').order('created_at', desc=True).limit(5).execute()
for p in picks.data:
    print(f'{p[\"ticker\"]}: {p[\"action\"]} - {p[\"confidence\"]:.1%}')
"
```

---

## ⚙️ 调整配置（可选）

### 如果还想监控其他群

编辑 `config/monitored_sources.yaml`：

```yaml
wechat_groups:
  exact_names:
    - "180K - 星球讨论群🪙"
    - "另一个股票群"        # 添加更多群
    - "投资学习群"
```

### 如果想过滤只处理包含特定词的消息

```yaml
filters:
  content_keywords:
    - "涨停"
    - "买入"
    - "卖出"
    - "推荐"
```

### 如果想排除更多广告词

```yaml
filters:
  exclude_keywords:
    - "广告"
    - "推广"
    - "加微信"
    - "扫码"
```

---

## 💡 实用技巧

### 技巧1：快速测试

```bash
# 创建测试文件
cat > test_180k.txt << 'EOF'
[2025-01-17 10:30:00] 测试: 贵州茅台600519涨停
[2025-01-17 10:35:00] 测试: 宁德时代300750也不错
EOF

# 测试处理
python examples/wechat_input_example.py
```

### 技巧2：批量历史数据

```bash
# 如果要导入历史数据
# 按日期组织文件
data/wechat/exports/
├── 180k_20250110.json
├── 180k_20250111.json
├── 180k_20250112.json
└── ...

# 批量导入
cp data/wechat/exports/180k_*.json data/wechat/auto_exports/
```

### 技巧3：定时导出提醒

在手机/电脑设置每天提醒：
```
每天 23:00
导出"180K - 星球讨论群🪙"今日消息
```

---

## ❓ 常见问题

**Q: 群名包含emoji会影响吗？**
A: 不会，系统完全支持emoji，已配置精确匹配

**Q: 必须要时间戳吗？**
A: 不是必须的，系统会自动生成

**Q: 可以只导出部分消息吗？**
A: 可以，只复制你想要的消息即可

**Q: 图片必须要OCR吗？**
A: 不是必须的，如果只有文字消息就不需要

**Q: 多久处理一次？**
A: 自动收集器默认每5分钟检查一次新文件

---

## 📚 相关文档

- **图片PDF处理**: `IMAGE_PDF_QUICKSTART.md`
- **自动收集**: `AUTO_COLLECTION_QUICKSTART.md`
- **手动导出**: `EXPORT_QUICKSTART.md`
- **配置文件**: `config/monitored_sources.yaml`

---

## ✨ 总结

你的系统现在专门配置为监控 **"180K - 星球讨论群🪙"**

**最简单的使用**：
```bash
# 1. 从PC微信复制今天的消息
# 2. 粘贴到文件并整理格式
# 3. 复制到监控目录
cp my_messages.txt data/wechat/auto_exports/

# 完成！系统自动处理
```

**完整功能**：
```bash
# 1. 用WeChatMsg导出（包含图片和PDF）
# 2. 复制到监控目录
cp -r 180k_export data/wechat/auto_exports/

# 系统会：
# - OCR识别图片
# - 提取PDF
# - 分析讨论
# - 生成推荐
```

开始使用吧！🚀
