#!/usr/bin/env python3
"""
AI Research Monitor - 主程序

自动监控 Twitter/Reddit，分析内容，生成深度报告
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.twitter_scraper import TwitterScraper
from scrapers.reddit_scraper import RedditScraper
from analyzers.content_analyzer import ContentAnalyzer
from generators.article_generator import ArticleGenerator


def load_config(config_path="config/config.yaml"):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def scrape_content(config):
    """抓取内容"""
    print("=" * 60)
    print("开始抓取内容...")
    print("=" * 60)

    all_content = []

    # 抓取 Reddit
    if config['monitoring']['reddit']:
        print("\n[Reddit] 开始抓取...")
        reddit_scraper = RedditScraper()
        subreddits = config['monitoring']['reddit']['subreddits']
        reddit_posts = reddit_scraper.scrape_multiple_subreddits(
            subreddits,
            sort_by=config['monitoring']['reddit']['sort_by'],
            limit_per_subreddit=config['monitoring']['reddit']['fetch_limit']
        )
        all_content.extend(reddit_posts)
        print(f"[Reddit] 共抓取 {len(reddit_posts)} 篇帖子")

    # 抓取 Twitter
    if config['monitoring']['twitter']:
        print("\n[Twitter] 开始抓取...")
        twitter_scraper = TwitterScraper(
            use_alternative=config['monitoring']['twitter'].get('use_alternative', True)
        )

        # 抓取关键账号
        key_accounts = config['monitoring']['twitter']['key_accounts']
        tweets = twitter_scraper.scrape_multiple_users(
            key_accounts,
            max_results_per_user=5
        )
        all_content.extend(tweets)
        print(f"[Twitter] 共抓取 {len(tweets)} 条推文")

    print(f"\n总共抓取 {len(all_content)} 条内容")
    return all_content


def analyze_content(content_items, config):
    """分析内容"""
    print("\n" + "=" * 60)
    print("开始分析内容...")
    print("=" * 60)

    llm_provider = config['generation']['llm_provider']
    analyzer = ContentAnalyzer(llm_provider=llm_provider)

    # 分析和筛选
    analyzed_items = analyzer.analyze_content(content_items)

    print(f"\n筛选出 {len(analyzed_items)} 条高价值内容（评分 >= 6.5）")

    # 找出热门话题
    topics = analyzer.find_trending_topics(analyzed_items, top_n=5)

    print("\n热门话题：")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic['topic']} (出现{topic['count']}次, 平均评分{topic['avg_score']:.1f})")

    return analyzed_items, topics


def generate_articles(topics, analyzed_items, config):
    """生成文章"""
    print("\n" + "=" * 60)
    print("开始生成文章...")
    print("=" * 60)

    llm_provider = config['generation']['llm_provider']
    generator = ArticleGenerator(llm_provider=llm_provider)

    output_dir = config['output']['directory']
    daily_articles = config['generation']['daily_articles']

    # 根据配置决定生成多少篇文章
    if isinstance(daily_articles, str) and '-' in daily_articles:
        min_articles, max_articles = map(int, daily_articles.split('-'))
        num_articles = min(max_articles, len(topics))
    else:
        num_articles = min(int(daily_articles), len(topics))

    generated_files = []

    for i, topic_info in enumerate(topics[:num_articles], 1):
        print(f"\n正在生成第 {i} 篇文章: {topic_info['topic']}")

        # 获取该话题相关的内容
        related_items = topic_info['related_items'][:5]  # 取前5个最相关的

        # 生成文章
        article = generator.generate_article(
            topic=topic_info['topic'],
            content_items=related_items,
            article_type="deep_analysis",
            length=config['generation'].get('article_length', 'medium')
        )

        # 保存文章
        timestamp = datetime.now().strftime("%Y%m%d")
        topic_slug = topic_info['topic'].replace(' ', '_').replace('/', '-')
        filename = f"{timestamp}_{topic_slug}_analysis.md"

        file_path = generator.save_article(article, output_dir=output_dir, filename=filename)
        generated_files.append(file_path)

        print(f"✓ 文章已保存: {file_path}")

    return generated_files


def main():
    """主函数"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          AI Research Monitor - AI 研究监控系统            ║
    ║                                                           ║
    ║    自动追踪 Twitter/Reddit AI 动态，生成深度分析报告      ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # 加载环境变量
    load_dotenv()

    # 加载配置
    try:
        config = load_config()
    except FileNotFoundError:
        print("错误: 配置文件 config/config.yaml 不存在")
        print("请参考 config/config.yaml.example 创建配置文件")
        return

    # 1. 抓取内容
    content_items = scrape_content(config)

    if not content_items:
        print("\n警告: 未抓取到任何内容，请检查API配置")
        return

    # 2. 分析内容
    analyzed_items, topics = analyze_content(content_items, config)

    if not topics:
        print("\n未发现值得深入研究的话题")
        return

    # 3. 生成文章
    generated_files = generate_articles(topics, analyzed_items, config)

    # 完成
    print("\n" + "=" * 60)
    print("✓ 任务完成！")
    print("=" * 60)
    print(f"\n共生成 {len(generated_files)} 篇文章：")
    for file_path in generated_files:
        print(f"  - {file_path}")

    print(f"\n所有文章保存在: {config['output']['directory']}")
    print("\n建议下一步: 审阅文章，添加图片，发布到公众号")


if __name__ == "__main__":
    main()
