"""WeChat export parser - Supports multiple export formats."""

import json
import csv
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger


def parse_wechat_export(export_path: str, export_type: str = "auto") -> List[Dict[str, Any]]:
    """
    Parse WeChat export file.

    Supported formats:
    - JSON: Standard JSON array of message objects
    - CSV: CSV file with message data
    - TXT: Simple text format with sender and message
    - Directory: Multiple JSON/TXT files

    Args:
        export_path: Path to export file/directory
        export_type: Type of export (auto, json, csv, txt)

    Returns:
        List of parsed messages in standardized format

    Message format:
    {
        "message_id": str,
        "chat_id": str,
        "chat_name": str,
        "sender": str,
        "sender_id": str,
        "content": str,
        "timestamp": str (ISO format),
        "message_type": str (text, image, link, etc.),
        "attachments": dict,
        "links": list,
        "mentions": list,
        "is_group": bool
    }
    """
    logger.info(f"Parsing WeChat export: {export_path}")

    path = Path(export_path)

    # Auto-detect format
    if export_type == "auto":
        if path.is_dir():
            export_type = "directory"
        elif path.suffix == ".json":
            export_type = "json"
        elif path.suffix == ".csv":
            export_type = "csv"
        elif path.suffix == ".txt":
            export_type = "txt"
        else:
            logger.warning(f"Unknown format for {export_path}, trying JSON")
            export_type = "json"

    # Parse based on format
    if export_type == "json":
        return _parse_json_export(path)
    elif export_type == "csv":
        return _parse_csv_export(path)
    elif export_type == "txt":
        return _parse_txt_export(path)
    elif export_type == "directory":
        return _parse_directory_export(path)
    else:
        logger.error(f"Unsupported export type: {export_type}")
        return []


def _parse_json_export(file_path: Path) -> List[Dict[str, Any]]:
    """Parse JSON format export."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            messages = data
        elif isinstance(data, dict):
            # Try common keys
            messages = (data.get('messages') or
                       data.get('data') or
                       data.get('chats', [{}])[0].get('messages', []))
        else:
            logger.error(f"Unexpected JSON structure in {file_path}")
            return []

        parsed = []
        for i, msg in enumerate(messages):
            parsed_msg = _standardize_message(msg, message_id=f"msg_{i}")
            if parsed_msg:
                parsed.append(parsed_msg)

        logger.info(f"Parsed {len(parsed)} messages from JSON")
        return parsed

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Error parsing JSON {file_path}: {e}")
        return []


def _parse_csv_export(file_path: Path) -> List[Dict[str, Any]]:
    """Parse CSV format export."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            messages = list(reader)

        parsed = []
        for i, msg in enumerate(messages):
            parsed_msg = _standardize_message(msg, message_id=f"msg_{i}")
            if parsed_msg:
                parsed.append(parsed_msg)

        logger.info(f"Parsed {len(parsed)} messages from CSV")
        return parsed

    except Exception as e:
        logger.error(f"Error parsing CSV {file_path}: {e}")
        return []


def _parse_txt_export(file_path: Path) -> List[Dict[str, Any]]:
    """
    Parse simple TXT format export.

    Expected format:
    [2025-01-15 10:30:00] 张三: 贵州茅台今天涨停了
    [2025-01-15 10:31:00] 李四: 看好后续表现
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Regex pattern for common WeChat export format
        pattern = r'\[(.+?)\]\s*(.+?)[:：]\s*(.+)'

        parsed = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line)
            if match:
                timestamp_str, sender, content = match.groups()

                # Parse timestamp
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except:
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y/%m/%d %H:%M:%S")
                    except:
                        timestamp = datetime.now()

                msg = {
                    "message_id": f"msg_{i}",
                    "chat_id": file_path.stem,
                    "chat_name": file_path.stem,
                    "sender": sender.strip(),
                    "sender_id": f"user_{hash(sender) % 10000}",
                    "content": content.strip(),
                    "timestamp": timestamp.isoformat(),
                    "message_type": "text",
                    "attachments": {},
                    "links": _extract_links(content),
                    "mentions": [],
                    "is_group": True
                }
                parsed.append(msg)

        logger.info(f"Parsed {len(parsed)} messages from TXT")
        return parsed

    except Exception as e:
        logger.error(f"Error parsing TXT {file_path}: {e}")
        return []


def _parse_directory_export(dir_path: Path) -> List[Dict[str, Any]]:
    """Parse directory containing multiple export files."""
    all_messages = []

    for file_path in dir_path.glob("*"):
        if file_path.is_file():
            if file_path.suffix == ".json":
                messages = _parse_json_export(file_path)
            elif file_path.suffix == ".csv":
                messages = _parse_csv_export(file_path)
            elif file_path.suffix == ".txt":
                messages = _parse_txt_export(file_path)
            else:
                continue

            all_messages.extend(messages)

    logger.info(f"Parsed {len(all_messages)} messages from directory")
    return all_messages


def _standardize_message(msg: Dict[str, Any], message_id: str = None) -> Optional[Dict[str, Any]]:
    """
    Standardize message format from various sources.

    Handles different field names and formats.
    """
    # Extract content (try different field names)
    content = (msg.get('content') or
               msg.get('message') or
               msg.get('text') or
               msg.get('msg') or
               msg.get('body') or
               "")

    if not content:
        return None

    # Extract timestamp
    timestamp = msg.get('timestamp') or msg.get('time') or msg.get('date')
    if timestamp:
        if isinstance(timestamp, int):
            # Unix timestamp
            timestamp = datetime.fromtimestamp(timestamp).isoformat()
        elif not isinstance(timestamp, str):
            timestamp = str(timestamp)
    else:
        timestamp = datetime.now().isoformat()

    # Extract sender
    sender = (msg.get('sender') or
              msg.get('from') or
              msg.get('user') or
              msg.get('username') or
              "Unknown")

    # Build standardized message
    standardized = {
        "message_id": msg.get('message_id') or msg.get('id') or message_id or f"msg_{hash(content) % 100000}",
        "chat_id": msg.get('chat_id') or msg.get('group_id') or "default_chat",
        "chat_name": msg.get('chat_name') or msg.get('group_name') or "WeChat Group",
        "sender": sender,
        "sender_id": msg.get('sender_id') or msg.get('user_id') or f"user_{hash(sender) % 10000}",
        "content": str(content),
        "timestamp": timestamp,
        "message_type": msg.get('message_type') or msg.get('type') or _detect_message_type(content),
        "attachments": msg.get('attachments') or {},
        "links": msg.get('links') or _extract_links(str(content)),
        "mentions": msg.get('mentions') or [],
        "is_group": msg.get('is_group', True)
    }

    return standardized


def _detect_message_type(content: str) -> str:
    """Detect message type from content."""
    if "[图片]" in content or "[Image]" in content:
        return "image"
    elif "[链接]" in content or "http" in content:
        return "link"
    elif "[文件]" in content or "[File]" in content:
        return "file"
    else:
        return "text"


def _extract_links(text: str) -> List[str]:
    """Extract URLs from text."""
    url_pattern = r'https?://[^\s\u4e00-\u9fff]+'
    links = re.findall(url_pattern, text)
    return links


def parse_wechat_article(url: str) -> Dict[str, Any]:
    """
    Parse WeChat public account article.

    TODO: Implement web scraping for WeChat articles
    Requires handling of JavaScript rendering and anti-scraping measures.
    """
    logger.info(f"Parsing WeChat article: {url}")

    # Placeholder - implement with requests + BeautifulSoup or Selenium
    return {
        "url": url,
        "title": "",
        "author": "",
        "content": "",
        "published_at": "",
        "images": [],
    }
