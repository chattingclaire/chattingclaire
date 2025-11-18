#!/usr/bin/env python3
"""
监控源配置助手

交互式配置要监控的微信群聊和公众号
"""

import yaml
from pathlib import Path


def main():
    print("=" * 60)
    print("微信监控源配置助手")
    print("=" * 60)
    print()

    config = {
        "wechat_groups": {
            "name_keywords": [],
            "exact_names": [],
            "group_ids": []
        },
        "wechat_official_accounts": {
            "accounts": [],
            "rss_feeds": []
        },
        "filters": {
            "enable_group_filter": True,
            "enable_account_filter": True,
            "content_keywords": [],
            "exclude_keywords": []
        }
    }

    # ===== 配置群聊 =====
    print("📱 第1步：配置微信群聊")
    print("-" * 60)
    print()

    choice = input("你想监控所有群聊，还是只监控特定群？\n1. 所有群聊\n2. 只监控特定群\n请选择 (1/2): ").strip()

    if choice == "1":
        config["filters"]["enable_group_filter"] = False
        print("✓ 已配置为监控所有群聊\n")

    else:
        print("\n你可以通过以下方式指定要监控的群：")
        print("1. 群名关键词（推荐）- 例如：包含'股票'的所有群")
        print("2. 完整群名 - 例如：'价值投资交流群'")
        print()

        # 关键词方式
        keywords = input("请输入群名关键词（多个用逗号分隔，留空跳过）：").strip()
        if keywords:
            config["wechat_groups"]["name_keywords"] = [k.strip() for k in keywords.split(",")]
            print(f"✓ 已添加关键词: {', '.join(config['wechat_groups']['name_keywords'])}")

        # 完整群名
        exact_names = input("\n请输入完整群名（多个用逗号分隔，留空跳过）：").strip()
        if exact_names:
            config["wechat_groups"]["exact_names"] = [n.strip() for n in exact_names.split(",")]
            print(f"✓ 已添加群聊: {', '.join(config['wechat_groups']['exact_names'])}")

        if not keywords and not exact_names:
            print("⚠ 未添加任何群聊，将监控所有群")
            config["filters"]["enable_group_filter"] = False

    print()

    # ===== 配置公众号 =====
    print("📰 第2步：配置公众号")
    print("-" * 60)
    print()

    accounts = input("请输入要监控的公众号（多个用逗号分隔，留空跳过）：").strip()
    if accounts:
        config["wechat_official_accounts"]["accounts"] = [a.strip() for a in accounts.split(",")]
        print(f"✓ 已添加公众号: {', '.join(config['wechat_official_accounts']['accounts'])}")
    else:
        print("跳过公众号配置")
        config["filters"]["enable_account_filter"] = False

    print()

    # ===== 内容过滤 =====
    print("🔍 第3步：内容过滤（可选）")
    print("-" * 60)
    print()

    content_filter = input("是否只处理包含特定关键词的消息？(y/n): ").strip().lower()

    if content_filter == "y":
        keywords = input("请输入关键词（多个用逗号分隔）：").strip()
        if keywords:
            config["filters"]["content_keywords"] = [k.strip() for k in keywords.split(",")]
            print(f"✓ 只处理包含这些词的消息: {', '.join(config['filters']['content_keywords'])}")

    exclude = input("\n是否要排除包含某些词的消息（如广告）？(y/n): ").strip().lower()

    if exclude == "y":
        keywords = input("请输入要排除的词（多个用逗号分隔）：").strip()
        if keywords:
            config["filters"]["exclude_keywords"] = [k.strip() for k in keywords.split(",")]
            print(f"✓ 将忽略包含这些词的消息: {', '.join(config['filters']['exclude_keywords'])}")

    print()

    # ===== 保存配置 =====
    print("=" * 60)
    print("配置摘要")
    print("=" * 60)

    if config["filters"]["enable_group_filter"]:
        if config["wechat_groups"]["name_keywords"]:
            print(f"群聊关键词: {', '.join(config['wechat_groups']['name_keywords'])}")
        if config["wechat_groups"]["exact_names"]:
            print(f"精确群名: {', '.join(config['wechat_groups']['exact_names'])}")
    else:
        print("群聊: 监控所有")

    if config["filters"]["enable_account_filter"] and config["wechat_official_accounts"]["accounts"]:
        print(f"公众号: {', '.join(config['wechat_official_accounts']['accounts'])}")
    else:
        print("公众号: 未配置")

    if config["filters"]["content_keywords"]:
        print(f"内容关键词: {', '.join(config['filters']['content_keywords'])}")

    if config["filters"]["exclude_keywords"]:
        print(f"排除关键词: {', '.join(config['filters']['exclude_keywords'])}")

    print()

    # 保存
    save = input("是否保存配置？(y/n): ").strip().lower()

    if save == "y":
        config_path = Path("config/monitored_sources.yaml")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        print(f"\n✓ 配置已保存到: {config_path}")
        print("\n下一步:")
        print("1. 启动自动收集器: ./start_auto_collector.sh")
        print("2. 导出微信消息并放到: data/wechat/auto_exports/")
        print("3. 系统会自动过滤并处理配置的群聊和公众号")

    else:
        print("\n配置未保存")
        print(f"你可以手动编辑: config/monitored_sources.yaml")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消配置")
    except Exception as e:
        print(f"\n错误: {e}")
