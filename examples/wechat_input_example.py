#!/usr/bin/env python3
"""
微信消息输入示例

展示如何将微信消息导入到系统中的3种方法。
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime


# ============================================================================
# 示例1：创建示例数据文件
# ============================================================================

def create_sample_data():
    """创建示例微信数据文件"""
    print("=" * 60)
    print("示例1：创建测试数据")
    print("=" * 60)

    # 确保目录存在
    data_dir = Path("data/wechat/examples")
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. JSON格式（推荐）
    json_data = [
        {
            "sender": "张三",
            "content": "贵州茅台今天涨停了，基本面持续向好，看好后续表现",
            "timestamp": "2025-01-15T10:30:00",
            "chat_name": "股票交流群"
        },
        {
            "sender": "李四",
            "content": "600519目标价2800，白酒板块整体走强",
            "timestamp": "2025-01-15T10:35:00",
            "chat_name": "股票交流群"
        },
        {
            "sender": "王五",
            "content": "茅台Q4业绩超预期，营收同比增长15%，建议关注",
            "timestamp": "2025-01-15T11:00:00",
            "chat_name": "股票交流群"
        },
        {
            "sender": "赵六",
            "content": "五粮液000858也不错，可以考虑配置",
            "timestamp": "2025-01-15T14:30:00",
            "chat_name": "股票交流群"
        },
        {
            "sender": "孙七",
            "content": "白酒板块整体估值合理，长期看好龙头企业",
            "timestamp": "2025-01-15T15:00:00",
            "chat_name": "股票交流群"
        },
        {
            "sender": "周八",
            "content": "宁德时代300750也值得关注，新能源赛道长期利好",
            "timestamp": "2025-01-15T16:00:00",
            "chat_name": "股票交流群"
        }
    ]

    json_file = data_dir / "sample_messages.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"✓ 创建JSON文件: {json_file}")

    # 2. TXT格式
    txt_content = """[2025-01-15 10:30:00] 张三: 贵州茅台今天涨停了，基本面持续向好，看好后续表现
[2025-01-15 10:35:00] 李四: 600519目标价2800，白酒板块整体走强
[2025-01-15 11:00:00] 王五: 茅台Q4业绩超预期，营收同比增长15%，建议关注
[2025-01-15 14:30:00] 赵六: 五粮液000858也不错，可以考虑配置
[2025-01-15 15:00:00] 孙七: 白酒板块整体估值合理，长期看好龙头企业
[2025-01-15 16:00:00] 周八: 宁德时代300750也值得关注，新能源赛道长期利好
"""

    txt_file = data_dir / "sample_messages.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    print(f"✓ 创建TXT文件: {txt_file}")

    # 3. CSV格式
    csv_content = """sender,content,timestamp,chat_name
张三,贵州茅台今天涨停了，基本面持续向好，看好后续表现,2025-01-15T10:30:00,股票交流群
李四,600519目标价2800，白酒板块整体走强,2025-01-15T10:35:00,股票交流群
王五,茅台Q4业绩超预期，营收同比增长15%，建议关注,2025-01-15T11:00:00,股票交流群
赵六,五粮液000858也不错，可以考虑配置,2025-01-15T14:30:00,股票交流群
孙七,白酒板块整体估值合理，长期看好龙头企业,2025-01-15T15:00:00,股票交流群
周八,宁德时代300750也值得关注，新能源赛道长期利好,2025-01-15T16:00:00,股票交流群
"""

    csv_file = data_dir / "sample_messages.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    print(f"✓ 创建CSV文件: {csv_file}")

    print(f"\n示例数据已创建在: {data_dir}/")
    return json_file, txt_file, csv_file


# ============================================================================
# 示例2：测试Parser
# ============================================================================

def test_parser():
    """测试WeChat parser"""
    print("\n" + "=" * 60)
    print("示例2：测试Parser")
    print("=" * 60)

    from tools.datasources.wechat_parser import parse_wechat_export

    # 创建测试数据
    json_file, txt_file, csv_file = create_sample_data()

    # 测试JSON
    print("\n测试JSON格式...")
    messages = parse_wechat_export(str(json_file), export_type="json")
    print(f"✓ 解析了 {len(messages)} 条消息")

    if messages:
        print("\n第一条消息示例:")
        msg = messages[0]
        print(f"  发送者: {msg['sender']}")
        print(f"  内容: {msg['content'][:50]}...")
        print(f"  时间: {msg['timestamp']}")
        print(f"  提取的股票代码: {msg['metadata']['extracted_tickers']}")

    # 测试TXT
    print("\n测试TXT格式...")
    messages = parse_wechat_export(str(txt_file), export_type="txt")
    print(f"✓ 解析了 {len(messages)} 条消息")

    # 测试CSV
    print("\n测试CSV格式...")
    messages = parse_wechat_export(str(csv_file), export_type="csv")
    print(f"✓ 解析了 {len(messages)} 条消息")

    # 测试自动检测
    print("\n测试自动格式检测...")
    messages = parse_wechat_export(str(json_file), export_type="auto")
    print(f"✓ 自动检测并解析了 {len(messages)} 条消息")

    return messages


# ============================================================================
# 示例3：使用WxSourceAgent处理
# ============================================================================

def test_wx_agent():
    """测试WxSourceAgent"""
    print("\n" + "=" * 60)
    print("示例3：使用WxSourceAgent")
    print("=" * 60)

    from agents.wx_source.agent import WxSourceAgent

    # 创建测试数据
    json_file, _, _ = create_sample_data()

    # 创建agent
    print("\n创建WxSourceAgent...")
    wx_agent = WxSourceAgent()

    # 处理微信导出
    print(f"处理文件: {json_file}")
    results = wx_agent.run(
        wechat_export_path=str(json_file),
        export_type="json",
        process_images=False,
        process_links=False
    )

    print(f"\n处理结果:")
    print(f"  总消息数: {results['total_messages']}")
    print(f"  已处理: {results['processed_messages']}")
    print(f"  文章数: {results['processed_articles']}")
    print(f"  成功率: {results['success_rate']:.1%}")


# ============================================================================
# 示例4：使用Memory API索引
# ============================================================================

def test_memory_indexing():
    """测试直接索引到Memory系统"""
    print("\n" + "=" * 60)
    print("示例4：索引到Memory系统")
    print("=" * 60)

    from memory.enhanced_context import get_enhanced_context_manager

    # 获取context manager
    print("初始化Context Manager...")
    ctx = get_enhanced_context_manager()

    # 准备消息
    messages = [
        {
            "message_id": "msg_001",
            "content": "贵州茅台今天涨停了，基本面持续向好",
            "sender": "张三",
            "timestamp": "2025-01-15T10:30:00",
            "chat_id": "group_123"
        },
        {
            "message_id": "msg_002",
            "content": "600519目标价2800，白酒板块整体走强",
            "sender": "李四",
            "timestamp": "2025-01-15T10:35:00",
            "chat_id": "group_123"
        },
        {
            "message_id": "msg_003",
            "content": "茅台Q4业绩超预期，建议关注",
            "sender": "王五",
            "timestamp": "2025-01-15T11:00:00",
            "chat_id": "group_123"
        }
    ]

    # 批量索引
    print(f"\n索引 {len(messages)} 条消息...")
    try:
        indexed_count = ctx.index_wechat_messages(
            messages=messages,
            batch_size=100
        )
        print(f"✓ 成功索引 {indexed_count} 条消息")

        # 测试搜索
        print("\n测试搜索...")
        results = ctx.search_similar_content(
            query="贵州茅台",
            source_filter="wx_raw_messages",
            limit=5,
            threshold=0.5
        )

        print(f"✓ 找到 {len(results)} 条相关消息")

        for i, result in enumerate(results[:3], 1):
            print(f"\n{i}. 相似度: {result['similarity_score']:.2f}")
            print(f"   内容: {result['content'][:80]}...")

    except Exception as e:
        print(f"⚠ 索引失败（可能需要先启动数据库）: {e}")


# ============================================================================
# 示例5：运行完整Pipeline
# ============================================================================

async def test_full_pipeline():
    """测试完整的交易流程"""
    print("\n" + "=" * 60)
    print("示例5：运行完整Pipeline")
    print("=" * 60)

    from orchestrator import TradingOrchestrator

    # 创建测试数据
    json_file, _, _ = create_sample_data()

    # 创建orchestrator
    print("\n初始化Trading Orchestrator...")
    orchestrator = TradingOrchestrator(config={
        "initial_capital": 100000,
    })

    # 运行pipeline（只收集信号，不执行交易）
    print(f"处理文件: {json_file}")
    print("运行模式: signals_only（只生成信号）\n")

    try:
        results = await orchestrator.run_pipeline(
            wechat_export_path=str(json_file),
            mode="signals_only"
        )

        print("=" * 60)
        print("Pipeline执行结果")
        print("=" * 60)

        # 微信处理结果
        if 'wx_source' in results['agent_results']:
            wx_stats = results['agent_results']['wx_source']
            print(f"\n✓ 微信Source Agent:")
            print(f"  处理消息: {wx_stats['processed_messages']} 条")
            print(f"  成功率: {wx_stats['success_rate']:.1%}")

        # 外部信号结果
        if 'external_source' in results['agent_results']:
            ext_stats = results['agent_results']['external_source']
            print(f"\n✓ 外部Source Agent:")
            print(f"  收集信号: {ext_stats.get('total_items', 0)} 条")

        # 股票选择结果
        if 'stock_picks' in results:
            picks = results['stock_picks']
            print(f"\n✓ Selection Agent:")
            print(f"  生成推荐: {len(picks)} 只股票\n")

            for i, pick in enumerate(picks[:5], 1):
                print(f"{i}. {pick['ticker']} - {pick['action']}")
                print(f"   置信度: {pick['confidence']:.1%}")
                print(f"   微信权重: {pick['wx_weight']:.1%}")
                print(f"   目标价: ¥{pick.get('target_price', 'N/A')}")
                print(f"   原因: {', '.join(pick['reasons'][:2])}")
                print()

    except Exception as e:
        print(f"⚠ Pipeline执行失败: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("微信消息输入完整示例")
    print("=" * 60)
    print(f"时间: {datetime.now().isoformat()}\n")

    # 示例1：创建测试数据
    json_file, txt_file, csv_file = create_sample_data()

    # 示例2：测试Parser
    messages = test_parser()

    # 示例3：测试WxSourceAgent
    try:
        test_wx_agent()
    except Exception as e:
        print(f"⚠ WxSourceAgent测试失败: {e}")

    # 示例4：测试Memory索引
    try:
        test_memory_indexing()
    except Exception as e:
        print(f"⚠ Memory索引测试失败（可能需要配置数据库）: {e}")

    # 示例5：运行完整Pipeline
    try:
        asyncio.run(test_full_pipeline())
    except Exception as e:
        print(f"⚠ Pipeline测试失败: {e}")

    print("\n" + "=" * 60)
    print("示例运行完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 查看创建的示例文件: data/wechat/examples/")
    print("2. 修改为你自己的微信数据")
    print("3. 运行完整流程")
    print("\n详细文档: docs/WECHAT_USAGE.md")


if __name__ == "__main__":
    main()
