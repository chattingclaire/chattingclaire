# AI Research Monitor - AI 研究监控与深度报告生成系统

一个为 AI 商业科技媒体和投资人设计的智能内容监控系统，自动追踪 Twitter/Reddit 上的 AI 和具身智能动态，生成深度分析报告。

## 功能特点

- 🔍 **智能监控**: 自动抓取 Twitter 和 Reddit 上的 AI、具身智能相关内容
- 🧠 **内容筛选**: AI 驱动的内容价值评估，识别值得深入研究的话题
- 📝 **深度报告**: 自动生成公众号格式的深度分析文章
- 💼 **投资视角**: 结合商业洞察和投资分析角度
- ⚡ **每日简报**: 定时生成每日重点内容摘要

## 项目结构

```
ai_research_monitor/
├── scrapers/          # 数据抓取模块
│   ├── twitter_scraper.py
│   └── reddit_scraper.py
├── analyzers/         # 内容分析模块
│   └── content_analyzer.py
├── generators/        # 报告生成模块
│   ├── article_generator.py
│   └── system_prompt.md
├── config/           # 配置文件
│   ├── config.yaml
│   └── keywords.yaml
├── outputs/          # 输出目录
└── main.py           # 主程序
```

## 快速开始

### 1. 安装依赖

```bash
cd ai_research_monitor
pip install -r requirements.txt
```

### 2. 配置环境变量

复制示例环境变量文件并填入你的 API 密钥：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API keys
```

需要的 API Keys：
- **Anthropic Claude API** 或 **OpenAI API**（用于内容分析和文章生成）
- **Reddit API**（Client ID 和 Secret）
- **Twitter API**（可选，推荐使用替代方案）

### 3. 配置监控参数

编辑 `config/config.yaml`：

```yaml
# 修改关注的账号、subreddits、关键词等
monitoring:
  twitter:
    key_accounts: ["AndrewYNg", "karpathy", "OpenAI"]
  reddit:
    subreddits: ["MachineLearning", "artificial"]
```

### 4. 运行系统

```bash
# 手动运行一次
python main.py

# 或者使其可执行
chmod +x main.py
./main.py
```

### 5. 设置定时任务（可选）

使用 cron 设置每日自动运行：

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天早上 9 点运行）
0 9 * * * cd /path/to/ai_research_monitor && python main.py
```

## 使用说明

### 工作流程

1. **内容抓取**: 从 Twitter 和 Reddit 抓取 AI 相关内容
2. **智能筛选**: 使用 AI 评估内容价值（技术、商业、投资维度）
3. **话题识别**: 识别热门话题和趋势
4. **文章生成**: 基于 system prompt 生成深度分析文章
5. **输出保存**: 保存为公众号可用的 Markdown 格式

### System Prompt 风格

文章生成器使用精心设计的 system prompt，确保输出符合以下风格：

- ✅ 克制理性、客观公正、数据驱动
- ✅ 多重视角：投资人 + 产品经理 + 工程师 + 研究员
- ✅ 深度洞察、直击本质、犀利幽默
- ✅ 拒绝吹嘘、远离广告、不用营销话术
- ❌ 禁止"不是...而是..."、"范式"、"从...到..."等表达

参考示例：`examples/reference_article_minimax.md`

### 自定义配置

编辑 `config/config.yaml` 可以自定义：

- 监控的 Twitter 账号和 Reddit subreddits
- 内容筛选阈值（最低评分、互动量）
- 文章生成数量和长度
- 使用的 LLM 模型（Claude vs GPT-4）

## 输出示例

生成的文章将保存在 `outputs/` 目录，文件名格式：

```
20250115_具身智能_analysis.md
20250115_AI融资_analysis.md
```

文章包含：
- 标题（20字以内，数据驱动）
- 开篇（100字内，直接切入核心）
- 多个分析板块（使用"XXX —— 当XXX做到XXX"的小标题）
- 数据对比、竞品分析、投资视角
- 参考资料链接

## 模块说明

### scrapers/

- `twitter_scraper.py`: 抓取 Twitter 内容（支持官方 API 或替代方案）
- `reddit_scraper.py`: 抓取 Reddit 帖子

### analyzers/

- `content_analyzer.py`: 使用 AI 评估内容价值，筛选高质量话题

### generators/

- `article_generator.py`: 基于 system prompt 生成深度分析文章
- `system_prompt.md`: 详细的写作风格指南和示例

### config/

- `config.yaml`: 主配置文件
- `.env`: API 密钥（不提交到 git）

## 常见问题

**Q: Twitter API 太贵怎么办？**

A: 设置 `use_alternative: true`，可以使用免费的替代方案（如 nitter、snscrape）

**Q: 如何调整文章风格？**

A: 编辑 `generators/system_prompt.md`，修改写作指南和示例

**Q: 生成的文章质量不理想？**

A:
1. 检查输入内容的质量（提高筛选阈值）
2. 调整 system prompt 的具体要求
3. 尝试不同的 LLM 模型（Claude vs GPT-4）
4. 在 `config.yaml` 中调整文章长度和类型

**Q: 如何添加更多数据源？**

A: 在 `scrapers/` 目录创建新的抓取器，参考现有代码结构

## 贡献与反馈

欢迎提交 Issue 和 Pull Request！

## License

MIT License
