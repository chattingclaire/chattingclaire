"""
Twitter/X 内容抓取器

注意: 由于 Twitter API 收费政策变化，这里提供两个选项：
1. 使用官方 API（需要付费）
2. 使用替代方案（如 nitter, snscrape 等）
"""

import os
import tweepy
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class TwitterScraper:
    """Twitter 内容抓取器"""

    def __init__(self, bearer_token=None, use_alternative=False):
        """
        初始化 Twitter 抓取器

        Args:
            bearer_token: Twitter API Bearer Token
            use_alternative: 是否使用替代方案（推荐）
        """
        self.bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        self.use_alternative = use_alternative or os.getenv("TWITTER_USE_ALTERNATIVE", "true").lower() == "true"

        if not self.use_alternative and self.bearer_token:
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
            except Exception as e:
                print(f"Twitter API 初始化失败: {e}")
                self.client = None
        else:
            self.client = None
            print("使用替代抓取方案（建议手动实现或使用第三方工具）")

    def scrape_user_tweets(
        self,
        username: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        抓取指定用户的推文

        Args:
            username: Twitter 用户名
            max_results: 最大返回数量

        Returns:
            推文列表
        """
        if not self.client:
            return self._scrape_with_alternative(username, max_results)

        tweets = []

        try:
            # 获取用户 ID
            user = self.client.get_user(username=username)
            if not user.data:
                print(f"用户 @{username} 不存在")
                return []

            user_id = user.data.id

            # 获取推文
            response = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'text']
            )

            if response.data:
                for tweet in response.data:
                    metrics = tweet.public_metrics
                    tweets.append({
                        "source": "Twitter",
                        "title": f"@{username}: {tweet.text[:100]}...",
                        "content": tweet.text,
                        "url": f"https://twitter.com/{username}/status/{tweet.id}",
                        "metadata": {
                            "author": f"@{username}",
                            "timestamp": tweet.created_at.isoformat(),
                            "engagement": f"{metrics['like_count']} likes, {metrics['retweet_count']} RTs",
                            "likes": metrics['like_count'],
                            "retweets": metrics['retweet_count'],
                            "replies": metrics['reply_count']
                        }
                    })

        except Exception as e:
            print(f"抓取 @{username} 的推文失败: {e}")

        return tweets

    def scrape_search(
        self,
        query: str,
        max_results: int = 50
    ) -> List[Dict]:
        """
        搜索推文

        Args:
            query: 搜索关键词
            max_results: 最大返回数量

        Returns:
            推文列表
        """
        if not self.client:
            return []

        tweets = []

        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API 限制
                tweet_fields=['created_at', 'public_metrics', 'author_id']
            )

            if response.data:
                for tweet in response.data:
                    metrics = tweet.public_metrics
                    tweets.append({
                        "source": "Twitter",
                        "title": tweet.text[:100] + "...",
                        "content": tweet.text,
                        "url": f"https://twitter.com/i/status/{tweet.id}",
                        "metadata": {
                            "author": f"user_{tweet.author_id}",
                            "timestamp": tweet.created_at.isoformat(),
                            "engagement": f"{metrics['like_count']} likes, {metrics['retweet_count']} RTs",
                            "likes": metrics['like_count'],
                            "retweets": metrics['retweet_count']
                        }
                    })

        except Exception as e:
            print(f"搜索推文失败: {e}")

        return tweets

    def scrape_multiple_users(
        self,
        usernames: List[str],
        max_results_per_user: int = 5
    ) -> List[Dict]:
        """
        抓取多个用户的推文

        Args:
            usernames: 用户名列表
            max_results_per_user: 每个用户的最大推文数

        Returns:
            所有推文列表
        """
        all_tweets = []

        for username in usernames:
            print(f"正在抓取 @{username} 的推文...")
            tweets = self.scrape_user_tweets(username, max_results_per_user)
            all_tweets.extend(tweets)

        return all_tweets

    def _scrape_with_alternative(self, username: str, max_results: int) -> List[Dict]:
        """
        使用替代方案抓取（占位函数）

        实际使用时可以集成：
        - nitter（开源 Twitter 前端）
        - snscrape（命令行工具）
        - 或其他第三方服务
        """
        print(f"替代抓取方案：请手动实现或使用第三方工具抓取 @{username}")
        print("建议工具: nitter, snscrape, 或浏览器自动化")

        # 返回空列表（实际使用时替换为真实实现）
        return []


# 使用示例
if __name__ == "__main__":
    scraper = TwitterScraper()

    # 抓取关键账号
    key_accounts = ["AndrewYNg", "karpathy", "OpenAI"]

    tweets = scraper.scrape_multiple_users(key_accounts, max_results_per_user=5)

    print(f"共抓取 {len(tweets)} 条推文")
    for tweet in tweets[:3]:
        print(f"\n{tweet['metadata']['author']}: {tweet['content'][:100]}")
        print(f"互动: {tweet['metadata']['engagement']}")
