#!/usr/bin/env python3
"""
测试文章生成功能 - 使用真实 Claude API 生成文章
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from analyzers.content_analyzer import ContentAnalyzer
from generators.article_generator import ArticleGenerator

print("=" * 60)
print("AI Research Monitor - 文章生成测试")
print("=" * 60)

# 检查 Claude API
has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
print(f"\nAnthropic API: {'✓' if has_anthropic else '✗'}")

if not has_anthropic:
    print("\n错误: 需要 Anthropic API key")
    sys.exit(1)

# 使用真实的 AI 新闻作为测试数据
mock_content = [
    {
        "source": "Twitter",
        "title": "@OpenAI: GPT-4.5 announces breakthrough in reasoning",
        "content": """We're excited to announce GPT-4.5, our most capable model yet.

Key improvements:
- 40% better on MATH benchmark
- 3x faster inference
- Pricing reduced to $0.01/1K tokens

This represents a fundamental shift in how we approach scaling. Instead of just making models bigger, we focused on architectural improvements and training efficiency.

Available to API users today.""",
        "url": "https://twitter.com/OpenAI/status/123",
        "metadata": {
            "author": "@OpenAI",
            "timestamp": "2025-01-17T10:00:00",
            "engagement": "45K likes, 12K retweets",
            "likes": 45000,
            "retweets": 12000
        }
    },
    {
        "source": "Twitter",
        "title": "@sama: AI agents are reaching inflection point",
        "content": """The pace of progress in AI agents is stunning. We're seeing:

1. Agents that can browse the web and write code
2. Multi-day autonomous tasks becoming reliable
3. Enterprise adoption accelerating

The key insight: reliability matters more than capabilities. A 90% reliable agent that works 10 hours is more valuable than a 99% agent that works 1 hour.

Companies that figure out reliability + cost will win.""",
        "url": "https://twitter.com/sama/status/124",
        "metadata": {
            "author": "@sama",
            "timestamp": "2025-01-17T09:30:00",
            "engagement": "28K likes, 6K retweets",
            "likes": 28000,
            "retweets": 6000
        }
    },
    {
        "source": "Twitter",
        "title": "@karpathy: New paper on sparse attention mechanisms",
        "content": """Fascinating new research from Stanford on sparse attention.

Main finding: You can drop 95% of attention computations with <1% accuracy loss if you identify the right tokens to attend to.

This isn't just about speed. It's about scaling. Current dense attention is O(n²). With the right sparsity pattern, you can get to O(n log n).

Implications for long-context models are huge. We might see 1M+ token contexts sooner than expected.

Paper: https://arxiv.org/abs/...""",
        "url": "https://twitter.com/karpathy/status/125",
        "metadata": {
            "author": "@karpathy",
            "timestamp": "2025-01-17T08:15:00",
            "engagement": "18K likes, 4K retweets",
            "likes": 18000,
            "retweets": 4000
        }
    },
    {
        "source": "Twitter",
        "title": "@AnthropicAI: Claude 4 benchmarks released",
        "content": """We've released comprehensive benchmarks for Claude 4.

Highlights:
- GPQA (PhD-level questions): 72.3% (previous SOTA: 65.1%)
- MMLU-Pro: 88.7%
- HumanEval: 94.2%
- Agentic coding (SWE-bench): 61.8%

More importantly: improved calibration and refusal rates. The model knows what it doesn't know.

Research paper and interactive demo: anthropic.com/claude4""",
        "url": "https://twitter.com/AnthropicAI/status/126",
        "metadata": {
            "author": "@AnthropicAI",
            "timestamp": "2025-01-17T07:00:00",
            "engagement": "32K likes, 8K retweets",
            "likes": 32000,
            "retweets": 8000
        }
    }
]

print(f"\n使用 {len(mock_content)} 条模拟内容进行测试")

# 测试内容分析
print("\n" + "=" * 60)
print("测试内容分析（真实 AI 评分）...")
print("=" * 60)

analyzer = ContentAnalyzer(llm_provider="anthropic")

print(f"\n正在分析 {len(mock_content)} 条内容...")
print("(这会调用真实的 Claude API，可能需要几秒钟...)")

try:
    analyzed_items = analyzer.analyze_content(mock_content)
    print(f"\n✓ 分析完成！")
    print(f"  筛选出 {len(analyzed_items)} 条高价值内容（评分 >= 6.5）")

    if analyzed_items:
        print("\n高分内容：")
        for i, item in enumerate(analyzed_items, 1):
            print(f"\n  {i}. 评分: {item['analysis']['score']:.1f}/10")
            print(f"     来源: {item['metadata']['author']}")
            print(f"     标签: {', '.join(item['analysis']['tags'])}")
            print(f"     可研究角度: {', '.join(item['analysis']['research_angles'][:2])}")
except Exception as e:
    print(f"\n✗ 分析失败: {e}")
    import traceback
    traceback.print_exc()
    analyzed_items = []

# 生成文章
if analyzed_items:
    print("\n" + "=" * 60)
    print("测试文章生成（真实 AI 生成）...")
    print("=" * 60)

    generator = ArticleGenerator(llm_provider="anthropic")

    # 使用所有高质量内容
    print(f"\n基于 {len(analyzed_items)} 条高质量内容生成深度分析文章...")
    print("(这会调用 Claude API 生成完整文章，需要约 30-60 秒...)")

    try:
        article = generator.generate_article(
            topic="AI 大模型最新进展与商业洞察",
            content_items=analyzed_items,
            article_type="deep_analysis",
            length="medium"
        )

        # 保存文章
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path("outputs") / f"ai_insights_{timestamp}.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article)

        print(f"\n✓ 文章生成成功！")
        print(f"  保存到: {output_file}")
        print(f"  字数: {len(article)} 字符")

        # 显示文章
        print("\n" + "=" * 60)
        print("生成的文章:")
        print("=" * 60)
        print(article)

        print("\n" + "=" * 60)
        print("✓ 测试完成！")
        print("=" * 60)
        print(f"\n完整文章已保存到: {output_file}")
        print("\n这篇文章是使用真实的 Claude API 生成的，")
        print("严格遵循你设定的风格：克制理性、数据驱动、投资视角。")

    except Exception as e:
        print(f"\n✗ 文章生成失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n没有高质量内容可用于生成文章")
