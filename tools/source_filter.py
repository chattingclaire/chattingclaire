#!/usr/bin/env python3
"""
监控源过滤器

根据配置文件过滤微信群聊和公众号
"""

import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger


class SourceFilter:
    """监控源过滤器"""

    def __init__(self, config_path: str = "config/monitored_sources.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {self.config_path}")
            logger.info("使用默认配置（监控所有群聊）")
            return {
                "filters": {
                    "enable_group_filter": False,
                    "enable_account_filter": False
                }
            }

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            logger.info(f"✓ 加载配置: {self.config_path}")
            return config

        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {"filters": {"enable_group_filter": False}}

    def should_monitor_group(self, group_name: str, group_id: str = None) -> bool:
        """
        判断是否应该监控该群聊

        Args:
            group_name: 群名称
            group_id: 群ID（可选）

        Returns:
            bool: True = 应该监控, False = 忽略
        """
        # 如果未启用过滤，监控所有群
        if not self.config.get("filters", {}).get("enable_group_filter", False):
            return True

        groups_config = self.config.get("wechat_groups", {})

        # 1. 检查群ID（精确匹配，优先级最高）
        if group_id:
            group_ids = groups_config.get("group_ids", [])
            if group_ids and group_id in group_ids:
                logger.debug(f"✓ 群ID匹配: {group_name} ({group_id})")
                return True

        # 2. 检查精确名称
        exact_names = groups_config.get("exact_names", [])
        if exact_names and group_name in exact_names:
            logger.debug(f"✓ 群名精确匹配: {group_name}")
            return True

        # 3. 检查关键词
        keywords = groups_config.get("name_keywords", [])
        for keyword in keywords:
            if keyword in group_name:
                logger.debug(f"✓ 群名包含关键词 '{keyword}': {group_name}")
                return True

        # 都不匹配，忽略该群
        logger.debug(f"✗ 忽略群聊: {group_name}")
        return False

    def should_monitor_account(self, account_name: str) -> bool:
        """
        判断是否应该监控该公众号

        Args:
            account_name: 公众号名称

        Returns:
            bool: True = 应该监控, False = 忽略
        """
        # 如果未启用过滤，监控所有公众号
        if not self.config.get("filters", {}).get("enable_account_filter", False):
            return True

        accounts = self.config.get("wechat_official_accounts", {}).get("accounts", [])

        if not accounts:
            # 没有配置任何公众号，则不监控
            return False

        # 精确匹配或包含关键词
        for configured_account in accounts:
            if configured_account in account_name or account_name in configured_account:
                logger.debug(f"✓ 公众号匹配: {account_name}")
                return True

        logger.debug(f"✗ 忽略公众号: {account_name}")
        return False

    def should_process_message(self, content: str) -> bool:
        """
        判断是否应该处理该消息

        Args:
            content: 消息内容

        Returns:
            bool: True = 应该处理, False = 忽略
        """
        filters = self.config.get("filters", {})

        # 1. 检查排除关键词（优先级最高）
        exclude_keywords = filters.get("exclude_keywords", [])
        for keyword in exclude_keywords:
            if keyword in content:
                logger.debug(f"✗ 消息包含排除关键词 '{keyword}'")
                return False

        # 2. 检查内容关键词
        content_keywords = filters.get("content_keywords", [])

        # 如果没有配置内容关键词，则不过滤
        if not content_keywords:
            return True

        # 检查是否包含任一关键词
        for keyword in content_keywords:
            # 支持正则表达式
            try:
                if re.search(keyword, content):
                    logger.debug(f"✓ 消息包含关键词/匹配模式 '{keyword}'")
                    return True
            except re.error:
                # 不是正则表达式，当做普通字符串
                if keyword in content:
                    logger.debug(f"✓ 消息包含关键词 '{keyword}'")
                    return True

        logger.debug(f"✗ 消息不包含任何配置的关键词")
        return False

    def get_rss_feeds(self) -> List[str]:
        """获取配置的RSS订阅链接"""
        return self.config.get("wechat_official_accounts", {}).get("rss_feeds", [])

    def get_monitored_groups_summary(self) -> str:
        """获取监控群聊配置摘要"""
        if not self.config.get("filters", {}).get("enable_group_filter", False):
            return "监控所有群聊"

        groups_config = self.config.get("wechat_groups", {})
        summary = []

        exact_names = groups_config.get("exact_names", [])
        if exact_names:
            summary.append(f"{len(exact_names)} 个精确名称")

        keywords = groups_config.get("name_keywords", [])
        if keywords:
            summary.append(f"包含关键词: {', '.join(keywords)}")

        group_ids = groups_config.get("group_ids", [])
        if group_ids:
            summary.append(f"{len(group_ids)} 个群ID")

        return " | ".join(summary) if summary else "未配置"

    def get_monitored_accounts_summary(self) -> str:
        """获取监控公众号配置摘要"""
        if not self.config.get("filters", {}).get("enable_account_filter", False):
            return "监控所有公众号"

        accounts = self.config.get("wechat_official_accounts", {}).get("accounts", [])
        if accounts:
            return f"{len(accounts)} 个公众号: {', '.join(accounts[:3])}{'...' if len(accounts) > 3 else ''}"

        return "未配置"

    def print_config_summary(self):
        """打印配置摘要"""
        logger.info("=" * 60)
        logger.info("监控源配置摘要")
        logger.info("=" * 60)

        # 群聊配置
        logger.info(f"📱 微信群聊: {self.get_monitored_groups_summary()}")

        # 公众号配置
        logger.info(f"📰 公众号: {self.get_monitored_accounts_summary()}")

        # RSS订阅
        rss_feeds = self.get_rss_feeds()
        if rss_feeds:
            logger.info(f"🔗 RSS订阅: {len(rss_feeds)} 个")

        # 内容过滤
        filters = self.config.get("filters", {})
        content_keywords = filters.get("content_keywords", [])
        if content_keywords:
            logger.info(f"🔍 内容关键词: {', '.join(content_keywords[:5])}{'...' if len(content_keywords) > 5 else ''}")

        exclude_keywords = filters.get("exclude_keywords", [])
        if exclude_keywords:
            logger.info(f"🚫 排除关键词: {', '.join(exclude_keywords)}")

        logger.info("=" * 60)


# 全局实例
_filter_instance = None


def get_source_filter() -> SourceFilter:
    """获取全局过滤器实例"""
    global _filter_instance
    if _filter_instance is None:
        _filter_instance = SourceFilter()
    return _filter_instance


if __name__ == "__main__":
    """测试过滤器"""
    filter = SourceFilter()

    # 打印配置
    filter.print_config_summary()

    # 测试群聊过滤
    print("\n测试群聊过滤:")
    test_groups = [
        ("股票交流群", None),
        ("家人群", None),
        ("A股价值投资", None),
        ("同学聚会", None),
        ("量化交易讨论", None),
    ]

    for group_name, group_id in test_groups:
        should_monitor = filter.should_monitor_group(group_name, group_id)
        print(f"  {'✓' if should_monitor else '✗'} {group_name}")

    # 测试消息过滤
    print("\n测试消息过滤:")
    test_messages = [
        "贵州茅台600519今天涨停了",
        "明天吃什么",
        "推荐一个广告，加微信xxx",
        "建议关注宁德时代300750",
    ]

    for msg in test_messages:
        should_process = filter.should_process_message(msg)
        print(f"  {'✓' if should_process else '✗'} {msg[:30]}")
