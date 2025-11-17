"""WeChat Source Agent - Parse and extract WeChat information."""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

from agents.base_agent import BaseAgent
from tools.ocr import ocr_tool
from tools.cleaning import text_cleaner
from tools.datasources.wechat_parser import parse_wechat_export


class WxSourceAgent(BaseAgent):
    """
    Agent 1: WeChat Source Agent

    Responsible for parsing WeChat group chats and public account articles.
    This is the PRIMARY information source (weight >= 60%).
    """

    def __init__(self):
        super().__init__(
            agent_name="wx_source_agent",
            prompt_file="wx_source_agent.md",
        )

    def run(
        self,
        wechat_export_path: str,
        export_type: str = "auto",  # auto, html, json, db
        process_images: bool = True,
        process_links: bool = True,
    ) -> Dict[str, Any]:
        """
        Process WeChat exports and store in database.

        Args:
            wechat_export_path: Path to WeChat export file/directory
            export_type: Type of export (auto-detect if not specified)
            process_images: Whether to OCR images
            process_links: Whether to follow and extract linked articles

        Returns:
            Processing results with statistics
        """
        logger.info(f"Processing WeChat export: {wechat_export_path}")

        try:
            # Parse WeChat export
            messages = parse_wechat_export(wechat_export_path, export_type)
            logger.info(f"Parsed {len(messages)} messages from export")

            processed_messages = []
            processed_articles = []

            for msg in messages:
                try:
                    # Process message
                    processed = self._process_message(msg, process_images)
                    processed_messages.append(processed)

                    # Extract and process articles from links
                    if process_links and msg.get("links"):
                        for link in msg["links"]:
                            if self._is_wechat_article(link):
                                article = self._process_wechat_article(link)
                                if article:
                                    processed_articles.append(article)

                except Exception as e:
                    logger.warning(f"Error processing message {msg.get('message_id')}: {e}")
                    continue

            # Batch insert into database
            if processed_messages:
                self.db.insert_many("wx_raw_messages", processed_messages)
                logger.info(f"Inserted {len(processed_messages)} messages")

            if processed_articles:
                self.db.insert_many("wx_mp_articles", processed_articles)
                logger.info(f"Inserted {len(processed_articles)} articles")

            results = {
                "total_messages": len(messages),
                "processed_messages": len(processed_messages),
                "processed_articles": len(processed_articles),
                "success_rate": len(processed_messages) / len(messages) if messages else 0,
            }

            logger.info(f"WeChat processing complete: {results}")
            return results

        except Exception as e:
            logger.error(f"Error in WxSourceAgent.run: {e}")
            raise

    def _process_message(
        self, msg: Dict[str, Any], process_images: bool = True
    ) -> Dict[str, Any]:
        """Process a single WeChat message."""
        # Extract text content
        content = msg.get("content", "")

        # Clean text
        if content:
            content = text_cleaner.clean_chinese_text(content)

        # Process images with OCR
        ocr_text = ""
        if process_images and msg.get("message_type") == "image":
            image_path = msg.get("attachments", {}).get("images", [None])[0]
            if image_path:
                try:
                    ocr_result = ocr_tool.extract_text(image_path, lang="ch")
                    ocr_text = ocr_result.get("text", "")
                    content = f"{content}\n[OCR]: {ocr_text}"
                except Exception as e:
                    logger.warning(f"OCR failed for {image_path}: {e}")

        # Extract entities (tickers, companies)
        extracted = self._extract_entities(content)

        # Build metadata
        metadata = {
            "extracted_tickers": extracted.get("tickers", []),
            "companies": extracted.get("companies", []),
            "sentiment": self._analyze_sentiment(content),
            "topics": extracted.get("topics", []),
            "quality_score": self._calculate_quality_score(msg, content),
            "has_ocr": bool(ocr_text),
        }

        return {
            "chat_id": msg.get("chat_id"),
            "chat_name": msg.get("chat_name"),
            "message_id": msg.get("message_id"),
            "sender": msg.get("sender"),
            "sender_id": msg.get("sender_id"),
            "message_type": msg.get("message_type"),
            "content": content,
            "timestamp": msg.get("timestamp"),
            "attachments": msg.get("attachments"),
            "links": msg.get("links", []),
            "mentions": msg.get("mentions", []),
            "is_group": msg.get("is_group", True),
            "metadata": metadata,
        }

    def _process_wechat_article(self, url: str) -> Optional[Dict[str, Any]]:
        """Process a WeChat public account article."""
        try:
            # TODO: Implement article fetching and parsing
            # For now, return None (implement with web scraping/API)
            logger.info(f"Would process WeChat article: {url}")
            return None
        except Exception as e:
            logger.warning(f"Failed to process article {url}: {e}")
            return None

    def _is_wechat_article(self, url: str) -> bool:
        """Check if URL is a WeChat public account article."""
        return "mp.weixin.qq.com" in url

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract tickers, companies, and topics from text."""
        import re

        entities = {
            "tickers": [],
            "companies": [],
            "topics": [],
        }

        # Extract Chinese stock tickers (6 digits)
        cn_tickers = re.findall(r'\b[0-9]{6}\b', text)
        entities["tickers"].extend(cn_tickers)

        # Extract US stock tickers (capital letters, 1-5 chars)
        us_tickers = re.findall(r'\b[A-Z]{1,5}\b', text)
        # Filter common false positives
        us_tickers = [t for t in us_tickers if t not in ["I", "A", "OK", "WX"]]
        entities["tickers"].extend(us_tickers)

        # TODO: Implement company name extraction (NER)
        # TODO: Implement topic extraction

        return entities

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text (bullish/bearish/neutral)."""
        # Simple keyword-based sentiment (TODO: use LLM for better analysis)
        bullish_keywords = ["看好", "买入", "涨", "利好", "强势", "突破", "牛市"]
        bearish_keywords = ["看空", "卖出", "跌", "利空", "弱势", "破位", "熊市"]

        text_lower = text.lower()
        bullish_count = sum(1 for kw in bullish_keywords if kw in text_lower)
        bearish_count = sum(1 for kw in bearish_keywords if kw in text_lower)

        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        else:
            return "neutral"

    def _calculate_quality_score(self, msg: Dict[str, Any], content: str) -> float:
        """Calculate quality score for a message."""
        score = 0.5  # Base score

        # Length bonus
        if len(content) > 100:
            score += 0.1

        # Has ticker mention
        if any(char.isdigit() for char in content):
            score += 0.1

        # Has links (potentially article references)
        if msg.get("links"):
            score += 0.1

        # Not too short
        if len(content) < 10:
            score -= 0.2

        return max(0.0, min(1.0, score))
