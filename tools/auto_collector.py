#!/usr/bin/env python3
"""
微信自动收集器 - 简化版

支持多种数据源自动收集：
- 企业微信API（如果配置）
- 公众号RSS订阅
- 定时文件扫描（监控导出目录）
"""

import os
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger


class AutoCollector:
    """自动收集器"""

    def __init__(self):
        # 监控的导出目录
        self.watch_dir = Path(os.getenv("WECHAT_WATCH_DIR", "data/wechat/auto_exports"))
        self.watch_dir.mkdir(parents=True, exist_ok=True)

        # 已处理文件记录
        self.processed_files = set()
        self._load_processed_files()

        # Context manager
        from memory.enhanced_context import get_enhanced_context_manager
        self.ctx = get_enhanced_context_manager()

        logger.info(f"自动收集器初始化完成")
        logger.info(f"监控目录: {self.watch_dir}")

    def _load_processed_files(self):
        """加载已处理文件列表"""
        record_file = self.watch_dir / ".processed_files.txt"
        if record_file.exists():
            with open(record_file, 'r') as f:
                self.processed_files = set(line.strip() for line in f)
            logger.info(f"加载了 {len(self.processed_files)} 个已处理文件记录")

    def _save_processed_file(self, file_path: str):
        """记录已处理文件"""
        self.processed_files.add(file_path)
        record_file = self.watch_dir / ".processed_files.txt"
        with open(record_file, 'a') as f:
            f.write(f"{file_path}\n")

    def scan_new_files(self) -> List[Path]:
        """扫描新文件"""
        new_files = []

        for file_path in self.watch_dir.glob("*"):
            # 跳过隐藏文件和记录文件
            if file_path.name.startswith('.'):
                continue

            # 只处理支持的格式
            if file_path.suffix not in ['.json', '.csv', '.txt']:
                continue

            # 跳过已处理的文件
            if str(file_path) in self.processed_files:
                continue

            new_files.append(file_path)

        return new_files

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """处理单个文件"""
        logger.info(f"处理文件: {file_path.name}")

        try:
            from tools.datasources.wechat_parser import parse_wechat_export

            # 解析文件
            messages = parse_wechat_export(str(file_path), export_type="auto")

            if not messages:
                logger.warning(f"文件中没有消息: {file_path.name}")
                return {"success": False, "messages": 0}

            # 索引到系统
            indexed = self.ctx.index_wechat_messages(messages, batch_size=100)

            # 记录为已处理
            self._save_processed_file(str(file_path))

            logger.info(f"✓ {file_path.name}: 索引了 {indexed} 条消息")

            return {
                "success": True,
                "messages": indexed,
                "file": file_path.name
            }

        except Exception as e:
            logger.error(f"✗ 处理文件失败 {file_path.name}: {e}")
            return {"success": False, "error": str(e)}

    def collect_rss_feeds(self) -> int:
        """收集RSS订阅（如果配置）"""
        # 从环境变量读取RSS feeds
        rss_feeds_str = os.getenv("WECHAT_RSS_FEEDS")
        if not rss_feeds_str:
            return 0

        rss_feeds = rss_feeds_str.split(',')

        try:
            import feedparser
        except ImportError:
            logger.warning("feedparser未安装，跳过RSS收集（pip install feedparser）")
            return 0

        total_indexed = 0

        for feed_url in rss_feeds:
            feed_url = feed_url.strip()
            if not feed_url:
                continue

            try:
                logger.info(f"收集RSS: {feed_url[:50]}...")

                feed = feedparser.parse(feed_url)
                articles = []

                for entry in feed.entries:
                    articles.append({
                        "source_id": entry.get("id", entry.get("link")),
                        "source": "wechat_mp",
                        "content": f"{entry.get('title', '')}\n\n{entry.get('summary', '')}",
                        "url": entry.get("link"),
                        "published_at": entry.get("published", datetime.now().isoformat())
                    })

                if articles:
                    indexed = self.ctx.index_external_items(articles)
                    total_indexed += indexed
                    logger.info(f"✓ RSS索引了 {indexed} 篇文章")

            except Exception as e:
                logger.error(f"✗ RSS收集失败 {feed_url}: {e}")

        return total_indexed

    def collect_wecom_messages(self) -> int:
        """收集企业微信消息（如果配置）"""
        corp_id = os.getenv("WECOM_CORP_ID")
        if not corp_id:
            return 0

        try:
            from tools.datasources.wecom_receiver import WeComReceiver

            receiver = WeComReceiver(
                corp_id=os.getenv("WECOM_CORP_ID"),
                agent_id=os.getenv("WECOM_AGENT_ID"),
                secret=os.getenv("WECOM_SECRET")
            )

            messages = receiver.receive_messages()

            if messages:
                indexed = self.ctx.index_wechat_messages(messages)
                logger.info(f"✓ 企业微信索引了 {indexed} 条消息")
                return indexed

        except ImportError:
            logger.warning("企业微信receiver未实现，跳过")
        except Exception as e:
            logger.error(f"✗ 企业微信收集失败: {e}")

        return 0

    def run_collection_cycle(self) -> Dict[str, Any]:
        """运行一次收集周期"""
        logger.info("=" * 60)
        logger.info(f"开始收集周期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        stats = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "messages_indexed": 0,
            "rss_articles": 0,
            "wecom_messages": 0,
            "errors": []
        }

        # 1. 扫描并处理新文件
        try:
            new_files = self.scan_new_files()
            logger.info(f"发现 {len(new_files)} 个新文件")

            for file_path in new_files:
                result = self.process_file(file_path)
                if result["success"]:
                    stats["files_processed"] += 1
                    stats["messages_indexed"] += result["messages"]
                else:
                    stats["errors"].append(f"File {file_path.name}: {result.get('error', 'Unknown')}")

        except Exception as e:
            logger.error(f"文件扫描失败: {e}")
            stats["errors"].append(f"File scan: {str(e)}")

        # 2. 收集RSS订阅
        try:
            rss_count = self.collect_rss_feeds()
            stats["rss_articles"] = rss_count
        except Exception as e:
            logger.error(f"RSS收集失败: {e}")
            stats["errors"].append(f"RSS: {str(e)}")

        # 3. 收集企业微信
        try:
            wecom_count = self.collect_wecom_messages()
            stats["wecom_messages"] = wecom_count
        except Exception as e:
            logger.error(f"企业微信收集失败: {e}")
            stats["errors"].append(f"WeCom: {str(e)}")

        # 总结
        total = stats["messages_indexed"] + stats["rss_articles"] + stats["wecom_messages"]
        logger.info("=" * 60)
        logger.info(f"收集周期完成:")
        logger.info(f"  - 处理文件: {stats['files_processed']}")
        logger.info(f"  - 微信消息: {stats['messages_indexed']}")
        logger.info(f"  - RSS文章: {stats['rss_articles']}")
        logger.info(f"  - 企业微信: {stats['wecom_messages']}")
        logger.info(f"  - 总计: {total}")
        if stats["errors"]:
            logger.warning(f"  - 错误: {len(stats['errors'])} 个")
        logger.info("=" * 60)

        return stats

    def run_forever(self, interval_seconds: int = 300):
        """持续运行"""
        logger.info("🚀 自动收集器启动")
        logger.info(f"⏰ 收集间隔: {interval_seconds} 秒 ({interval_seconds//60} 分钟)")
        logger.info(f"📁 监控目录: {self.watch_dir.absolute()}")

        # 环境变量配置
        if os.getenv("WECHAT_RSS_FEEDS"):
            logger.info(f"📰 RSS订阅: 已配置")
        if os.getenv("WECOM_CORP_ID"):
            logger.info(f"💼 企业微信: 已配置")

        logger.info("\n使用提示:")
        logger.info("1. 将微信导出文件放到监控目录")
        logger.info("2. 支持 .json, .csv, .txt 格式")
        logger.info("3. 文件会自动处理并索引")
        logger.info("4. 已处理文件不会重复处理\n")

        cycle_count = 0

        while True:
            try:
                cycle_count += 1
                logger.info(f"\n第 {cycle_count} 次收集")

                stats = self.run_collection_cycle()

                # 如果有新内容，可以触发pipeline
                total = (stats["messages_indexed"] +
                        stats["rss_articles"] +
                        stats["wecom_messages"])

                if total > 0 and os.getenv("AUTO_RUN_PIPELINE") == "true":
                    logger.info("检测到新内容，触发Pipeline...")
                    try:
                        asyncio.run(self.trigger_pipeline())
                    except Exception as e:
                        logger.error(f"Pipeline触发失败: {e}")

            except KeyboardInterrupt:
                logger.info("\n收到中断信号，正在退出...")
                break
            except Exception as e:
                logger.error(f"收集周期出错: {e}")
                import traceback
                traceback.print_exc()

            # 等待下次收集
            logger.info(f"⏳ 等待 {interval_seconds} 秒...")
            time.sleep(interval_seconds)

        logger.info("自动收集器已停止")

    async def trigger_pipeline(self):
        """触发交易Pipeline（可选）"""
        from orchestrator import TradingOrchestrator

        orchestrator = TradingOrchestrator()

        results = await orchestrator.run_pipeline(
            wechat_export_path=None,  # 使用已索引的数据
            mode="signals_only"
        )

        logger.info(f"Pipeline完成: 生成了 {len(results.get('stock_picks', []))} 个推荐")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="微信自动收集器")
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="收集间隔（秒），默认300秒（5分钟）"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="只运行一次，不循环"
    )

    args = parser.parse_args()

    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()

    # 创建收集器
    collector = AutoCollector()

    if args.once:
        # 只运行一次
        logger.info("单次运行模式")
        collector.run_collection_cycle()
    else:
        # 持续运行
        collector.run_forever(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
