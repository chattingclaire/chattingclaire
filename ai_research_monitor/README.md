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
pip install -r requirements.txt
```

### 2. 配置 API Keys

编辑 `config/config.yaml`，填入你的 API 密钥：
- Twitter API (或使用 nitter/替代方案)
- Reddit API
- OpenAI API / Claude API

### 3. 运行监控

```bash
# 手动运行一次
python main.py

# 设置每日定时任务（可选）
# 使用 cron 或其他调度工具
```

## 使用说明

详细文档请参考各模块的说明。

## 输出格式

生成的文章将保存在 `outputs/` 目录，格式为公众号可直接使用的 Markdown 文档。
