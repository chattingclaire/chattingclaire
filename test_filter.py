#!/usr/bin/env python3
"""
测试群聊过滤配置

验证配置文件是否正确
"""

from tools.source_filter import get_source_filter


def main():
    print("=" * 60)
    print("群聊过滤配置测试")
    print("=" * 60)
    print()

    # 获取过滤器
    filter = get_source_filter()

    # 显示配置摘要
    filter.print_config_summary()

    # 测试群聊
    print("\n" + "=" * 60)
    print("测试群聊过滤")
    print("=" * 60)

    test_groups = [
        "180K - 星球讨论群🪙",      # 应该通过 ✓
        "家人群",                    # 应该被过滤 ✗
        "同学群",                    # 应该被过滤 ✗
        "星球投资讨论",              # 应该通过（包含"星球"）✓
        "工作讨论群",                # 应该通过（包含"讨论"）✓
        "朋友闲聊",                  # 应该被过滤 ✗
    ]

    print("\n测试结果：")
    for group_name in test_groups:
        should_monitor = filter.should_monitor_group(group_name)
        status = "✓ 监控" if should_monitor else "✗ 忽略"
        print(f"  {status} - {group_name}")

    # 测试消息过滤
    print("\n" + "=" * 60)
    print("测试消息内容过滤")
    print("=" * 60)

    test_messages = [
        "贵州茅台600519今天涨停了",
        "大家晚上吃什么",
        "推广一个广告产品",
        "建议关注宁德时代300750",
        "明天几点开会？",
    ]

    print("\n测试结果：")
    for msg in test_messages:
        should_process = filter.should_process_message(msg)
        status = "✓ 处理" if should_process else "✗ 忽略"
        print(f"  {status} - {msg}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("\n配置文件位置: config/monitored_sources.yaml")
    print("如需修改，编辑该文件即可")


if __name__ == "__main__":
    main()
