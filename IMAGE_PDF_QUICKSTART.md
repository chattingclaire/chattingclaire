# 处理图片和PDF - 快速指南

群里有图片和PDF？这样处理！

---

## 🚀 最简单方法（3步）

### 1️⃣ 用WeChatMsg导出

**Windows**:
1. 下载：https://github.com/LC044/WeChatMsg/releases
2. 运行 `WeChatMsg.exe`
3. 选择群聊
4. ✅ **勾选"导出图片"**
5. ✅ **勾选"导出附件"**
6. 导出为JSON

**Mac**:
```bash
git clone https://github.com/LC044/WeChatMsg.git
cd WeChatMsg
pip install -r requirements.txt
python main.py
```

### 2️⃣ 安装OCR和PDF工具

```bash
# 安装依赖（已在requirements.txt中）
pip install paddleocr pdfplumber PyPDF2 Pillow

# 测试OCR
python -c "
from paddleocr import PaddleOCR
print('✓ OCR已安装')
"

# 测试PDF
python -c "
import pdfplumber
print('✓ PDF处理已安装')
"
```

### 3️⃣ 启用图片和PDF处理

```bash
# 复制导出的数据（包含图片和PDF）
cp -r ~/Downloads/wechat_export data/wechat/auto_exports/

# 系统会自动：
# - OCR识别图片中的文字
# - 提取PDF内容
# - 索引所有信息
```

✅ **完成！**

---

## 📝 配置（可选）

编辑 `config/agents.yaml`：

```yaml
wx_source_agent:
  # 启用图片OCR
  process_images: true
  ocr_provider: "paddleocr"  # 免费，准确

  # 启用PDF处理
  process_pdfs: true

  # 过滤小图片（表情包）
  image_filters:
    min_size: 10000  # 10KB以上才处理
```

---

## 🎯 使用示例

### 场景1：群里发的K线图截图

**原始消息**：
```
张三 10:30
[图片：K线图.jpg]  # 显示"贵州茅台 突破2850"
```

**系统处理后**：
```
content: "[OCR] 贵州茅台 突破2850"
extracted_tickers: ["600519"]
```

### 场景2：群里的PDF研报

**原始消息**：
```
李四 14:00
[文件：茅台Q4财报.pdf]
```

**系统处理后**：
```
content: "贵州茅台2024年Q4财报摘要：
营收增长15%，净利润38.5亿，
ROE 32%，建议买入，目标价2800..."
```

---

## 🔍 验证是否工作

```python
# 查询OCR识别的内容
from memory.enhanced_context import get_enhanced_context_manager

ctx = get_enhanced_context_manager()

# 搜索图片中的内容
results = ctx.search_similar_content(
    query="K线图 突破",
    limit=10
)

for r in results:
    print(f"{r['similarity_score']:.2f} - {r['content'][:100]}")
```

---

## 💡 完整工作流

```bash
# 1. 导出（用WeChatMsg）
#    ✅ 勾选导出图片
#    ✅ 勾选导出附件

# 2. 复制到系统
cp -r ~/Downloads/my_group_export data/wechat/auto_exports/

# 3. 启动自动收集器
./start_auto_collector.sh

# 4. 等待几分钟（OCR需要时间）

# 5. 查询
python -c "
from memory.enhanced_context import get_enhanced_context_manager
ctx = get_enhanced_context_manager()
results = ctx.search_similar_content('贵州茅台', limit=5)
print(f'找到 {len(results)} 条相关内容')
"
```

---

## ⚠️ 注意事项

### 处理速度
- **图片OCR**：每张2-5秒
- **PDF提取**：每页1秒
- **建议**：第一次导出不要太多（<100张图片）

### 存储空间
- OCR只存文本，不存原图（节省空间）
- 可配置是否保留原始文件

### 识别准确率
- 中文：>95%
- 数字（股票代码）：>98%
- 模糊图片：可能识别不准

---

## 🛠️ 高级选项

### 选项1：使用在线OCR（更准确）

```bash
# .env 中添加腾讯OCR（可选）
TENCENT_OCR_SECRET_ID=your_id
TENCENT_OCR_SECRET_KEY=your_key

# 修改配置
# config/agents.yaml
ocr_provider: "tencent"  # 改为tencent
```

### 选项2：只处理特定类型图片

```yaml
# config/agents.yaml
image_filters:
  min_size: 50000        # 只处理50KB以上
  max_size: 10485760     # 不超过10MB
  allowed_types:
    - "jpg"
    - "png"
  # 过滤表情包和小图
```

---

## 📊 对比

| 方法 | 图片 | PDF | 难度 |
|-----|------|-----|------|
| 复制粘贴 | ❌ | ❌ | 简单 |
| WeChatMsg | ✅ | ✅ | 中等 |
| WeChatMsg + OCR | ✅✅ | ✅✅ | 推荐 |

---

## ✨ 总结

**如果群里有图片和PDF**：

1. 用 **WeChatMsg** 导出（勾选图片和附件）
2. 安装 **paddleocr** 和 **pdfplumber**
3. 放到 `data/wechat/auto_exports/`
4. 系统自动OCR+提取！

就这么简单！🎉

**详细文档**：`docs/HANDLE_IMAGES_PDF.md`
