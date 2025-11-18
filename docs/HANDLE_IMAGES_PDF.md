# 处理图片和PDF - 完整方案

群里有很多图片和PDF文件的处理方法。

---

## 🖼️ 问题：复制粘贴无法获取图片和PDF

**情况**：
- 微信群里发的截图（财报、K线图、研报）
- PDF文件（研究报告、公告）
- 图片中的文字内容

**解决方案**：使用工具导出 + OCR识别

---

## 方案1：用WeChatMsg导出（推荐）

### 为什么要用WeChatMsg？

✅ **可以导出图片**：保留所有图片文件
✅ **保留附件**：PDF、Word等文件
✅ **完整数据**：不丢失任何信息
✅ **支持OCR**：可以识别图片中的文字

### 使用步骤

#### 1. 安装WeChatMsg

**Windows**:
```
下载：https://github.com/LC044/WeChatMsg/releases
下载最新的 WeChatMsg.exe
```

**Mac/Linux**:
```bash
git clone https://github.com/LC044/WeChatMsg.git
cd WeChatMsg
pip install -r requirements.txt
python main.py
```

#### 2. 导出群聊（带图片）

1. 运行WeChatMsg
2. 左侧选择要导出的群聊
3. **重要**：勾选"导出图片"和"导出附件"
4. 选择导出格式：**JSON**（推荐）
5. 点击"导出"

#### 3. 导出结果

导出后会得到：
```
导出目录/
├── messages.json          # 消息内容
├── images/                # 所有图片
│   ├── img_001.jpg
│   ├── img_002.png
│   └── ...
└── files/                 # 所有附件
    ├── report.pdf
    ├── data.xlsx
    └── ...
```

#### 4. 处理导出数据

系统会自动处理这个目录：

```bash
# 将整个导出目录复制到系统
cp -r ~/Downloads/wechat_export data/wechat/auto_exports/

# 系统会：
# 1. 读取messages.json
# 2. OCR识别所有图片
# 3. 提取PDF文本
# 4. 索引所有内容
```

---

## 方案2：启用OCR和PDF处理

### 配置OCR（图片文字识别）

#### 选项A：使用PaddleOCR（免费，推荐）

```bash
# 1. 安装PaddleOCR
pip install paddlepaddle paddleocr

# 2. 测试
python -c "
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')
result = ocr.ocr('test_image.jpg')
print(result)
"
```

#### 选项B：使用腾讯OCR（在线API，精准）

```bash
# .env 中添加
TENCENT_OCR_SECRET_ID=your_secret_id
TENCENT_OCR_SECRET_KEY=your_secret_key
```

#### 选项C：使用EasyOCR

```bash
pip install easyocr
```

### 配置PDF处理

```bash
# 安装PDF处理库
pip install PyPDF2 pdfplumber

# 测试
python -c "
import pdfplumber
with pdfplumber.open('test.pdf') as pdf:
    text = pdf.pages[0].extract_text()
    print(text)
"
```

---

## 方案3：自动处理图片和PDF

### 更新Agent配置

编辑 `config/agents.yaml`：

```yaml
wx_source_agent:
  # 启用图片处理
  process_images: true
  ocr_provider: "paddleocr"  # paddleocr, tencent, easyocr

  # 启用PDF处理
  process_pdfs: true

  # 图片过滤（可选）
  image_filters:
    min_size: 10000  # 最小文件大小（字节），过滤表情包
    max_size: 10485760  # 最大10MB
    allowed_types:
      - "jpg"
      - "jpeg"
      - "png"

  # PDF过滤（可选）
  pdf_filters:
    max_pages: 100  # 最多处理100页
    max_size: 52428800  # 最大50MB
```

### 使用示例

```python
from agents.wx_source.agent import WxSourceAgent

# 创建agent
agent = WxSourceAgent()

# 处理包含图片和PDF的导出
results = agent.run(
    wechat_export_path="data/wechat/exports/group_chat",
    export_type="auto",
    process_images=True,   # ✅ 启用图片OCR
    process_links=True     # ✅ 抓取链接内容
)

print(f"处理消息: {results['processed_messages']}")
print(f"OCR图片: {results.get('processed_images', 0)}")
print(f"提取PDF: {results.get('processed_pdfs', 0)}")
```

---

## 方案4：针对特定类型的内容

### 场景1：群里主要是截图（K线图、财报）

**解决方案**：OCR + 关键词提取

```python
# WxSourceAgent 会自动：
# 1. 识别图片中的文字
# 2. 提取股票代码、数字、关键词
# 3. 将OCR结果作为消息内容索引

# 示例：
# 原图片：截图显示"贵州茅台 600519 涨停"
# 处理后：content = "[OCR] 贵州茅台 600519 涨停"
```

### 场景2：群里主要是PDF研报

**解决方案**：PDF提取 + 摘要

```python
# 系统会：
# 1. 提取PDF全文
# 2. 使用Claude生成摘要
# 3. 提取关键信息（股票代码、评级、目标价）

# 示例配置
config:
  pdf_processing:
    extract_summary: true      # 生成摘要
    extract_tables: true       # 提取表格数据
    extract_stock_codes: true  # 提取股票代码
```

### 场景3：混合内容（文字+图片+PDF）

**解决方案**：全部启用

```python
# 完整处理流程
results = agent.run(
    wechat_export_path="export_dir",
    process_images=True,        # OCR图片
    process_links=True,         # 抓取链接
    process_pdfs=True,          # 提取PDF
    extract_tables=True,        # 提取表格
    generate_summaries=True     # 生成摘要
)
```

---

## 实用示例

### 示例1：导出并处理一个研报群

```bash
# 1. 用WeChatMsg导出群聊
# 导出到：~/Downloads/research_group/

# 2. 复制到系统目录
cp -r ~/Downloads/research_group data/wechat/auto_exports/

# 3. 系统自动处理
# - 识别图片中的股票代码
# - 提取PDF研报内容
# - 索引到向量数据库

# 4. 查询
python -c "
from memory.enhanced_context import get_enhanced_context_manager
ctx = get_enhanced_context_manager()

# 搜索特定股票的研报
results = ctx.search_similar_content(
    query='贵州茅台 研报',
    source_filter='wx_raw_messages',
    limit=10
)

for r in results:
    print(f\"相似度: {r['similarity_score']:.2f}\")
    print(f\"内容: {r['content'][:100]}...\")
    print()
"
```

### 示例2：处理K线图截图

假设群里发了这样的消息：
```
张三 10:30
[图片：K线图.jpg]  # 图片显示"贵州茅台 日线 突破新高 2850"

李四 10:35
这个形态不错，可以关注
```

系统处理后：
```json
[
  {
    "sender": "张三",
    "content": "[OCR] 贵州茅台 日线 突破新高 2850",
    "message_type": "image",
    "metadata": {
      "extracted_tickers": ["600519"],
      "ocr_confidence": 0.95,
      "image_path": "images/img_001.jpg"
    }
  },
  {
    "sender": "李四",
    "content": "这个形态不错，可以关注",
    "message_type": "text"
  }
]
```

---

## 工具推荐

### 导出工具
1. **WeChatMsg** ⭐⭐⭐⭐⭐
   - 最推荐
   - 支持图片、PDF、视频
   - 开源免费

2. **WeChatExporter** ⭐⭐⭐⭐
   - Mac专用
   - 导出为HTML

### OCR工具
1. **PaddleOCR** ⭐⭐⭐⭐⭐
   - 免费
   - 中文识别准确
   - 本地运行

2. **腾讯OCR** ⭐⭐⭐⭐
   - 在线API
   - 精准度高
   - 需要付费

3. **EasyOCR** ⭐⭐⭐
   - 多语言支持
   - 安装简单

### PDF工具
1. **pdfplumber** ⭐⭐⭐⭐⭐
   - 推荐
   - 支持表格提取

2. **PyPDF2** ⭐⭐⭐
   - 轻量级
   - 基础功能

---

## 完整工作流

```bash
# ===== 安装依赖 =====
pip install paddleocr pdfplumber PyPDF2

# ===== 配置 =====
# 编辑 config/agents.yaml
vim config/agents.yaml
# 设置 process_images: true

# ===== 导出微信数据 =====
# 1. 运行 WeChatMsg
# 2. 选择群聊
# 3. ✅ 勾选"导出图片"
# 4. ✅ 勾选"导出附件"
# 5. 导出为JSON

# ===== 处理 =====
cp -r ~/Downloads/wechat_export data/wechat/auto_exports/

# 启动自动收集器
./start_auto_collector.sh

# ===== 等待处理 =====
# 系统会：
# 1. OCR所有图片
# 2. 提取所有PDF
# 3. 索引到数据库

# ===== 查询 =====
# 现在可以搜索图片和PDF中的内容了！
```

---

## 常见问题

**Q: OCR识别准确率如何？**
A: PaddleOCR中文识别率>95%，足够识别股票代码和关键信息

**Q: 处理速度慢吗？**
A: 本地OCR：每张图片2-5秒；PDF提取：每页1秒

**Q: 会存储原始图片吗？**
A: 可配置，默认只存OCR文本，节省空间

**Q: 支持表格提取吗？**
A: 支持！PDF中的表格会被提取为结构化数据

**Q: 手机截图能识别吗？**
A: 可以，只要导出时包含图片文件

---

## 总结

**最佳方案**：
1. ✅ 用 **WeChatMsg** 导出（包含图片和PDF）
2. ✅ 安装 **PaddleOCR** 和 **pdfplumber**
3. ✅ 启用 `process_images=True`
4. ✅ 放到监控目录，自动处理

这样就可以处理群里的所有内容了！🎉
