#!/usr/bin/env python3
"""
真实 API 测试 - 使用真实的 Twitter 和 Claude API
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

from scrapers.twitter_scraper import TwitterScraper
from analyzers.content_analyzer import ContentAnalyzer
from generators.article_generator import ArticleGenerator

print("=" * 60)
print("AI Research Monitor - 真实 API 测试")
print("=" * 60)

# 检查 API keys
print("\n检查 API Keys...")
has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
has_twitter = bool(os.getenv("TWITTER_BEARER_TOKEN"))

print(f"  Anthropic API: {'✓' if has_anthropic else '✗'}")
print(f"  Twitter API: {'✓' if has_twitter else '✗'}")

if not has_anthropic:
    print("\n错误: 需要 Anthropic API key")
    sys.exit(1)

# 测试 Twitter 抓取
print("\n" + "=" * 60)
print("测试 Twitter 抓取...")
print("=" * 60)

twitter_scraper = TwitterScraper(use_alternative=False)

# 只抓取一个账号，避免速率限制
test_accounts = ["karpathy"]  # 使用一个活跃账号测试

print(f"\n抓取 {len(test_accounts)} 个账号的推文（每个 5 条）...")

all_tweets = []
for account in test_accounts:
    print(f"  抓取 @{account}...")
    try:
        tweets = twitter_scraper.scrape_user_tweets(account, max_results=5)  # 最少5条
        all_tweets.extend(tweets)
        print(f"    ✓ 抓取到 {len(tweets)} 条推文")
    except Exception as e:
        print(f"    ✗ 失败: {e}")

print(f"\n共抓取 {len(all_tweets)} 条推文")

if not all_tweets:
    print("\n未抓取到内容，测试结束")
    sys.exit(0)

# 显示抓取的内容
print("\n示例推文：")
for i, tweet in enumerate(all_tweets[:3], 1):
    print(f"\n{i}. {tweet['metadata']['author']}")
    print(f"   {tweet['content'][:100]}...")
    print(f"   互动: {tweet['metadata']['engagement']}")

# 测试内容分析
print("\n" + "=" * 60)
print("测试内容分析（AI 评分）...")
print("=" * 60)

analyzer = ContentAnalyzer(llm_provider="anthropic")

print(f"\n分析 {len(all_tweets)} 条内容...")
try:
    analyzed_items = analyzer.analyze_content(all_tweets)
    print(f"✓ 筛选出 {len(analyzed_items)} 条高价值内容（评分 >= 6.5）")

    if analyzed_items:
        print("\n高分内容：")
        for item in analyzed_items[:3]:
            print(f"\n  评分: {item['analysis']['score']}/10")
            print(f"  内容: {item['content'][:80]}...")
            print(f"  标签: {', '.join(item['analysis']['tags'])}")
except Exception as e:
    print(f"✗ 分析失败: {e}")
    import traceback
    traceback.print_exc()
    analyzed_items = []

# 如果有高质量内容，生成文章
if analyzed_items:
    print("\n" + "=" * 60)
    print("测试文章生成...")
    print("=" * 60)

    generator = ArticleGenerator(llm_provider="anthropic")

    # 选择评分最高的 3 条内容
    top_items = analyzed_items[:3]

    print(f"\n基于 {len(top_items)} 条高质量内容生成文章...")

    try:
        article = generator.generate_article(
            topic="AI 领域最新动态",
            content_items=top_items,
            article_type="deep_analysis",
            length="medium"
        )

        # 保存文章
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path("outputs") / f"real_test_{timestamp}.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(article)

        print(f"\n✓ 文章生成成功！")
        print(f"  保存到: {output_file}")
        print(f"  长度: {len(article)} 字符")

        # 显示文章开头
        print("\n" + "-" * 60)
        print("文章预览：")
        print("-" * 60)
        print(article[:500] + "...")

    except Exception as e:
        print(f"\n✗ 文章生成失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("✓ 真实 API 测试完成！")
print("=" * 60)
