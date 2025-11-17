"""Text cleaning utilities."""

import re
from loguru import logger


def clean_chinese_text(text: str) -> str:
    """
    Clean Chinese text by removing unwanted characters.

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters but keep Chinese, English, digits, basic punctuation
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s.,!?;:()（）、，。！？；：]', '', text)

    return text.strip()


def normalize_ticker(ticker: str) -> str:
    """Normalize stock ticker format."""
    ticker = ticker.upper().strip()
    return ticker
