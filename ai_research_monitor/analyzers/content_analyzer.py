"""
内容分析器

使用 AI 分析和筛选值得深入研究的内容
"""

import os
from typing import List, Dict, Optional
import anthropic
import openai


class ContentAnalyzer:
    """内容分析器，评估内容价值并筛选值得深入研究的话题"""

    def __init__(self, llm_provider="anthropic", model=None):
        """
        初始化内容分析器

        Args:
            llm_provider: 使用的 LLM 提供商 ("anthropic" 或 "openai")
            model: 模型名称（可选）
        """
        self.llm_provider = llm_provider

        if llm_provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            self.model = model or "claude-sonnet-4-20250514"
        elif llm_provider == "openai":
            openai.api_key = os.getenv("OPENAI_API_KEY")
            self.model = model or "gpt-4-turbo-preview"
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    def analyze_content(self, content_items: List[Dict]) -> List[Dict]:
        """
        分析内容列表，筛选出值得深入研究的内容

        Args:
            content_items: 内容列表，每项包含 {source, title, content, url, metadata}

        Returns:
            筛选和排序后的内容列表，包含评分和分析
        """
        analyzed_items = []

        for item in content_items:
            # 分析单个内容
            analysis = self._analyze_single_item(item)

            if analysis['score'] >= 6.5:  # 只保留评分 >= 6.5 的内容
                item['analysis'] = analysis
                analyzed_items.append(item)

        # 按评分排序
        analyzed_items.sort(key=lambda x: x['analysis']['score'], reverse=True)

        return analyzed_items

    def _analyze_single_item(self, item: Dict) -> Dict:
        """
        分析单个内容项的价值

        Returns:
            {
                'score': float,  # 0-10分
                'reasoning': str,  # 评分理由
                'tags': List[str],  # 内容标签
                'research_angles': List[str]  # 可深入研究的角度
            }
        """
        prompt = f"""
请以 AI 商业科技投资人的角度，评估以下内容是否值得深入研究并撰写分析文章。

## 内容信息

**来源**: {item.get('source', 'Unknown')}
**标题**: {item.get('title', '')}
**内容**:
{item.get('content', '')[:1000]}

**元数据**:
- 时间: {item.get('metadata', {}).get('timestamp', 'Unknown')}
- 互动: {item.get('metadata', {}).get('engagement', 'N/A')}
- 作者: {item.get('metadata', {}).get('author', 'Unknown')}

## 评估维度

1. **技术价值** (0-10): 技术创新性、突破性、可复现性
2. **商业价值** (0-10): 市场规模、商业模式、变现潜力
3. **投资价值** (0-10): 融资情况、估值合理性、成长潜力
4. **内容质量** (0-10): 信息密度、数据充分性、独特性
5. **时效性** (0-10): 是否是最新动态、是否有时间窗口

## 输出格式

请以 JSON 格式输出：

{{
  "score": 7.5,
  "reasoning": "简要说明评分理由（100字内）",
  "tags": ["技术突破", "融资", "具身智能"],
  "research_angles": [
    "技术架构分析",
    "商业模式解读",
    "投资价值评估"
  ],
  "tech_score": 8,
  "business_score": 7,
  "investment_score": 7,
  "quality_score": 8,
  "timeliness_score": 8
}}

只输出 JSON，不要有其他文字。
"""

        try:
            if self.llm_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                result_text = response.content[0].text
            else:  # openai
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1000
                )
                result_text = response.choices[0].message.content

            # 解析 JSON
            import json
            # 提取 JSON（可能包含在代码块中）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]

            analysis = json.loads(result_text.strip())
            return analysis

        except Exception as e:
            print(f"分析失败: {e}")
            # 返回默认评分
            return {
                "score": 5.0,
                "reasoning": "分析失败，使用默认评分",
                "tags": [],
                "research_angles": [],
                "tech_score": 5,
                "business_score": 5,
                "investment_score": 5,
                "quality_score": 5,
                "timeliness_score": 5
            }

    def find_trending_topics(self, content_items: List[Dict], top_n: int = 5) -> List[Dict]:
        """
        从内容列表中识别热门话题

        Args:
            content_items: 内容列表
            top_n: 返回前 N 个话题

        Returns:
            话题列表，每个话题包含 {topic, count, related_items, summary}
        """
        # 先分析所有内容
        analyzed_items = self.analyze_content(content_items)

        # 提取所有标签
        all_tags = []
        for item in analyzed_items:
            all_tags.extend(item['analysis'].get('tags', []))

        # 统计标签频率
        from collections import Counter
        tag_counts = Counter(all_tags)

        # 构建话题
        topics = []
        for tag, count in tag_counts.most_common(top_n):
            related_items = [
                item for item in analyzed_items
                if tag in item['analysis'].get('tags', [])
            ]

            topics.append({
                'topic': tag,
                'count': count,
                'related_items': related_items,
                'avg_score': sum(item['analysis']['score'] for item in related_items) / len(related_items)
            })

        return topics


# 使用示例
if __name__ == "__main__":
    analyzer = ContentAnalyzer(llm_provider="anthropic")

    sample_content = [
        {
            "source": "Twitter",
            "title": "OpenAI 发布新模型",
            "content": "OpenAI 今天发布了新的多模态模型...",
            "url": "https://twitter.com/example",
            "metadata": {
                "timestamp": "2025-01-15",
                "engagement": "10K likes",
                "author": "@openai"
            }
        }
    ]

    # 分析内容
    analyzed = analyzer.analyze_content(sample_content)

    for item in analyzed:
        print(f"标题: {item['title']}")
        print(f"评分: {item['analysis']['score']}")
        print(f"理由: {item['analysis']['reasoning']}")
        print(f"标签: {item['analysis']['tags']}")
        print("---")
