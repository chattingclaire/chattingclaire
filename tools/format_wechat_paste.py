#!/usr/bin/env python3
"""
Mac微信粘贴内容格式化工具

从Mac微信复制的内容可能格式不规范，这个工具可以自动格式化。

使用方法：
    python tools/format_wechat_paste.py < pasted_content.txt
    或交互式输入
"""

import re
import sys
from datetime import datetime
from pathlib import Path


def parse_mac_wechat_paste(content: str) -> list:
    """
    解析Mac微信复制的内容

    支持多种格式：
    - 张三 10:30 消息内容
    - 10:30 张三: 消息内容
    - [张三] 10:30 消息内容
    """
    lines = content.strip().split('\n')
    messages = []

    # 正则模式
    patterns = [
        # 格式1: 张三 10:30 消息内容
        r'^(.+?)\s+(\d{1,2}:\d{2})\s+(.+)$',
        # 格式2: 10:30 张三: 消息内容
        r'^(\d{1,2}:\d{2})\s+(.+?)[:：]\s*(.+)$',
        # 格式3: [张三] 10:30 消息内容
        r'^\[(.+?)\]\s+(\d{1,2}:\d{2})\s+(.+)$',
        # 格式4: 张三: 消息内容 (没有时间)
        r'^(.+?)[:：]\s*(.+)$',
    ]

    current_date = datetime.now().strftime('%Y-%m-%d')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 尝试每个模式
        matched = False

        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()

                # 根据匹配的模式解析
                if len(groups) == 3:
                    if ':' in groups[0]:  # 时间在前
                        time_str = groups[0]
                        sender = groups[1]
                        content = groups[2]
                    elif ':' in groups[1]:  # 时间在中间
                        sender = groups[0]
                        time_str = groups[1]
                        content = groups[2]
                    else:  # [张三] 10:30 格式
                        sender = groups[0]
                        time_str = groups[1]
                        content = groups[2]

                    # 补全时间格式
                    if len(time_str.split(':')[0]) == 1:
                        time_str = '0' + time_str
                    timestamp = f"{current_date} {time_str}:00"

                elif len(groups) == 2:  # 没有时间
                    sender = groups[0]
                    content = groups[1]
                    timestamp = f"{current_date} {datetime.now().strftime('%H:%M:00')}"

                messages.append({
                    'timestamp': timestamp,
                    'sender': sender.strip(),
                    'content': content.strip()
                })
                matched = True
                break

        if not matched:
            # 可能是纯文本，归到上一条消息
            if messages:
                messages[-1]['content'] += '\n' + line

    return messages


def format_messages(messages: list) -> str:
    """格式化为标准格式"""
    output = []

    for msg in messages:
        formatted = f"[{msg['timestamp']}] {msg['sender']}: {msg['content']}"
        output.append(formatted)

    return '\n'.join(output)


def main():
    print("=" * 60)
    print("Mac微信粘贴内容格式化工具")
    print("=" * 60)
    print()
    print("请粘贴从Mac微信复制的内容（完成后按 Ctrl+D）：")
    print()

    # 读取输入
    content = sys.stdin.read()

    if not content.strip():
        print("没有输入内容")
        return

    # 解析
    print("\n解析中...\n")
    messages = parse_mac_wechat_paste(content)

    if not messages:
        print("未能解析出消息，请检查格式")
        return

    # 格式化
    formatted = format_messages(messages)

    # 显示结果
    print("=" * 60)
    print(f"解析到 {len(messages)} 条消息")
    print("=" * 60)
    print()
    print(formatted)
    print()

    # 保存选项
    save = input("是否保存到文件？(y/n): ").strip().lower()

    if save == 'y':
        # 默认文件名
        today = datetime.now().strftime('%Y%m%d')
        default_filename = f"180k_{today}.txt"

        filename = input(f"文件名 [{default_filename}]: ").strip()
        if not filename:
            filename = default_filename

        # 保存
        output_path = Path("data/wechat/auto_exports") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted)

        print(f"\n✓ 已保存到: {output_path}")
        print("\n系统会自动处理这个文件！")
    else:
        print("\n你可以手动复制上面的内容")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
