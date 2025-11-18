"""
AI 深度报告生成器

基于 system prompt 和筛选的内容，生成公众号格式的深度分析文章
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import anthropic
import openai


class ArticleGenerator:
    """文章生成器，使用 AI 生成深度分析文章"""

    def __init__(self, llm_provider="anthropic", model=None):
        """
        初始化文章生成器

        Args:
            llm_provider: 使用的 LLM 提供商 ("anthropic" 或 "openai")
            model: 模型名称（可选，不指定则使用默认模型）
        """
        self.llm_provider = llm_provider

        # 加载 system prompt
        system_prompt_path = Path(__file__).parent / "system_prompt.md"
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()

        # 初始化 LLM 客户端
        if llm_provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = model or "claude-3-5-sonnet-20241022"
        elif llm_provider == "openai":
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.model = model or "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    def generate_article(
        self,
        topic: str,
        content_items: List[Dict],
        article_type: str = "deep_analysis",
        length: str = "medium"
    ) -> str:
        """
        生成深度分析文章

        Args:
            topic: 文章主题
            content_items: 筛选后的内容列表，每项包含 {source, title, content, url, metadata}
            article_type: 文章类型 ("deep_analysis", "news_analysis", "trend_report")
            length: 文章长度 ("short", "medium", "long")

        Returns:
            生成的文章（Markdown 格式）
        """
        # 构建输入内容
        content_summary = self._summarize_content_items(content_items)

        # 生成文章
        user_prompt = self._build_user_prompt(topic, content_summary, article_type, length)

        if self.llm_provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )
            article = response.content[0].text
        else:  # openai
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            article = response.choices[0].message.content

        return article

    def _summarize_content_items(self, content_items: List[Dict]) -> str:
        """将内容列表整理成结构化摘要"""
        summary_parts = []

        for i, item in enumerate(content_items, 1):
            source = item.get('source', 'Unknown')
            title = item.get('title', 'No title')
            content = item.get('content', '')
            url = item.get('url', '')
            metadata = item.get('metadata', {})

            item_summary = f"""
## 来源 {i}: {source}

**标题**: {title}

**链接**: {url}

**内容摘要**:
{content[:500]}...

**元数据**:
- 发布时间: {metadata.get('timestamp', 'Unknown')}
- 互动数据: {metadata.get('engagement', 'N/A')}
- 作者: {metadata.get('author', 'Unknown')}
"""
            summary_parts.append(item_summary.strip())

        return "\n\n---\n\n".join(summary_parts)

    def _build_user_prompt(
        self,
        topic: str,
        content_summary: str,
        article_type: str,
        length: str
    ) -> str:
        """构建给 AI 的用户提示词"""

        length_guidance = {
            "short": "800-1200字，聚焦1个核心观点",
            "medium": "1500-2500字，展开2-3个核心观点",
            "long": "3000-5000字，深度分析多个维度"
        }

        type_guidance = {
            "deep_analysis": "深度技术和商业分析，包含实测验证、技术解读、商业价值、投资视角",
            "news_analysis": "新闻事件分析，快速解读核心信息、影响和意义",
            "trend_report": "行业趋势报告，分析多个事件的连接和趋势判断"
        }

        prompt = f"""
请基于以下信息，撰写一篇关于「{topic}」的{type_guidance.get(article_type, "深度分析")}文章。

## 文章要求

1. **长度**: {length_guidance.get(length, "1500-2500字")}
2. **格式**: 公众号 Markdown 格式，包含标题、小标题、段落、数据加粗、要点列表
3. **风格**: 严格遵循 system prompt 中的写作风格和规范

## 核心要点

- 开篇直接切入，用数据或场景吸引注意
- 每个判断都要有依据（数据、案例、对比）
- 提出独特洞察，不要简单搬运信息
- 从技术、商业、投资、场景多维度分析
- 使用"XXX —— 当XXX做到XXX"的小标题格式
- 严格禁止"不是...而是..."、"范式"、"从...到..."等表达
- 保持克制理性，避免营销话术和空洞形容

## 原始内容

{content_summary}

## 输出要求

请直接输出完整的 Markdown 格式文章，包括：
1. 文章标题（20字以内）
2. 开篇段落（100字内，直接切入核心）
3. 多个小标题板块（使用 ## 和 ###）
4. 参考资料部分

开始撰写吧！
"""
        return prompt.strip()

    def save_article(self, article: str, output_dir: str = "./outputs", filename: Optional[str] = None) -> str:
        """
        保存生成的文章

        Args:
            article: 文章内容
            output_dir: 输出目录
            filename: 文件名（可选，不指定则自动生成）

        Returns:
            保存的文件路径
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"article_{timestamp}.md"

        file_path = output_path / filename

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(article)

        return str(file_path)


# 使用示例
if __name__ == "__main__":
    # 初始化生成器
    generator = ArticleGenerator(llm_provider="anthropic")

    # 模拟筛选后的内容
    sample_content = [
        {
            "source": "Twitter",
            "title": "OpenAI发布新功能",
            "content": "OpenAI今天发布了...",
            "url": "https://twitter.com/example",
            "metadata": {
                "timestamp": "2025-01-15",
                "engagement": "1.2K likes, 300 retweets",
                "author": "@openai"
            }
        }
    ]

    # 生成文章
    article = generator.generate_article(
        topic="OpenAI 新功能分析",
        content_items=sample_content,
        article_type="deep_analysis",
        length="medium"
    )

    # 保存文章
    file_path = generator.save_article(article)
    print(f"文章已保存到: {file_path}")
