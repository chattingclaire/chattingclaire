"""
Reddit 内容抓取器
"""

import os
import praw
from datetime import datetime
from typing import List, Dict, Optional


class RedditScraper:
    """Reddit 内容抓取器"""

    def __init__(self, client_id=None, client_secret=None, user_agent="AI Research Monitor Bot"):
        """
        初始化 Reddit 抓取器

        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent字符串
        """
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent

        if self.client_id and self.client_secret:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent
            )
        else:
            self.reddit = None
            print("警告: Reddit API 凭证未设置，将无法抓取数据")

    def scrape_subreddit(
        self,
        subreddit_name: str,
        sort_by: str = "hot",
        limit: int = 50
    ) -> List[Dict]:
        """
        抓取指定 subreddit 的内容

        Args:
            subreddit_name: subreddit 名称
            sort_by: 排序方式 ("hot", "new", "top")
            limit: 抓取数量

        Returns:
            帖子列表
        """
        if not self.reddit:
            print("Reddit API 未初始化")
            return []

        posts = []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

            if sort_by == "hot":
                submissions = subreddit.hot(limit=limit)
            elif sort_by == "new":
                submissions = subreddit.new(limit=limit)
            elif sort_by == "top":
                submissions = subreddit.top(limit=limit, time_filter="day")
            else:
                submissions = subreddit.hot(limit=limit)

            for submission in submissions:
                post = {
                    "source": "Reddit",
                    "title": submission.title,
                    "content": submission.selftext,
                    "url": f"https://reddit.com{submission.permalink}",
                    "metadata": {
                        "subreddit": subreddit_name,
                        "author": str(submission.author),
                        "timestamp": datetime.fromtimestamp(submission.created_utc).isoformat(),
                        "engagement": f"{submission.score} upvotes, {submission.num_comments} comments",
                        "upvotes": submission.score,
                        "comments": submission.num_comments
                    }
                }
                posts.append(post)

        except Exception as e:
            print(f"抓取 r/{subreddit_name} 失败: {e}")

        return posts

    def scrape_multiple_subreddits(
        self,
        subreddit_names: List[str],
        sort_by: str = "hot",
        limit_per_subreddit: int = 20
    ) -> List[Dict]:
        """
        抓取多个 subreddits 的内容

        Args:
            subreddit_names: subreddit 名称列表
            sort_by: 排序方式
            limit_per_subreddit: 每个 subreddit 的抓取数量

        Returns:
            所有帖子列表
        """
        all_posts = []

        for subreddit_name in subreddit_names:
            print(f"正在抓取 r/{subreddit_name}...")
            posts = self.scrape_subreddit(subreddit_name, sort_by, limit_per_subreddit)
            all_posts.extend(posts)

        return all_posts


# 使用示例
if __name__ == "__main__":
    scraper = RedditScraper()

    # 抓取 AI 相关 subreddits
    subreddits = ["MachineLearning", "artificial", "LocalLLaMA"]

    posts = scraper.scrape_multiple_subreddits(subreddits, sort_by="hot", limit_per_subreddit=10)

    print(f"共抓取 {len(posts)} 篇帖子")
    for post in posts[:3]:
        print(f"\n标题: {post['title']}")
        print(f"来源: r/{post['metadata']['subreddit']}")
        print(f"互动: {post['metadata']['engagement']}")
