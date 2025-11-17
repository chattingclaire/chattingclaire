#!/bin/bash
#
# 启动微信自动收集器
#
# 使用方法：
#   ./start_auto_collector.sh              # 默认5分钟间隔
#   ./start_auto_collector.sh --interval 60   # 1分钟间隔
#   ./start_auto_collector.sh --once       # 只运行一次
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}微信自动收集器${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# 检查.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ 未找到 .env 文件${NC}"
    echo "正在创建示例配置..."
    cp .env.auto_collection.example .env
    echo -e "${GREEN}✓ 已创建 .env 文件${NC}"
    echo ""
    echo "请编辑 .env 文件并配置："
    echo "  1. WECHAT_WATCH_DIR - 监控目录"
    echo "  2. WECHAT_RSS_FEEDS - RSS订阅（可选）"
    echo "  3. WECOM_* - 企业微信（可选）"
    echo ""
    read -p "配置完成后按回车继续..."
fi

# 检查监控目录
WATCH_DIR=$(grep WECHAT_WATCH_DIR .env | cut -d '=' -f2)
if [ -z "$WATCH_DIR" ]; then
    WATCH_DIR="data/wechat/auto_exports"
fi

echo -e "${BLUE}检查监控目录...${NC}"
if [ ! -d "$WATCH_DIR" ]; then
    mkdir -p "$WATCH_DIR"
    echo -e "${GREEN}✓ 创建监控目录: $WATCH_DIR${NC}"
else
    echo -e "${GREEN}✓ 监控目录存在: $WATCH_DIR${NC}"
fi

# 检查依赖
echo -e "\n${BLUE}检查依赖...${NC}"
if ! python3 -c "import loguru" 2>/dev/null; then
    echo -e "${YELLOW}⚠ 缺少依赖，正在安装...${NC}"
    pip install -r requirements.txt
fi
echo -e "${GREEN}✓ 依赖已安装${NC}"

# 显示配置信息
echo -e "\n${BLUE}当前配置:${NC}"
echo "  监控目录: $WATCH_DIR"

if grep -q "^WECHAT_RSS_FEEDS=" .env 2>/dev/null; then
    RSS_COUNT=$(grep "^WECHAT_RSS_FEEDS=" .env | cut -d '=' -f2 | tr ',' '\n' | wc -l)
    echo -e "  RSS订阅: ${GREEN}已配置 ($RSS_COUNT 个)${NC}"
else
    echo "  RSS订阅: 未配置"
fi

if grep -q "^WECOM_CORP_ID=" .env 2>/dev/null; then
    echo -e "  企业微信: ${GREEN}已配置${NC}"
else
    echo "  企业微信: 未配置"
fi

# 使用说明
echo -e "\n${BLUE}使用说明:${NC}"
echo "1. 将微信导出文件放到: $WATCH_DIR/"
echo "2. 支持格式: .json, .csv, .txt"
echo "3. 系统会自动检测并处理新文件"
echo "4. 已处理的文件不会重复处理"
echo ""
echo "示例："
echo "  cp my_wechat_messages.json $WATCH_DIR/"
echo ""

# 启动收集器
echo -e "${GREEN}启动自动收集器...${NC}"
echo ""

python3 tools/auto_collector.py "$@"
