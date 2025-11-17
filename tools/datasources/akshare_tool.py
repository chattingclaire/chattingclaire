"""AKShare data source tool for comprehensive market data."""

import akshare as ak
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger
import pandas as pd


class AKShareDataSource:
    """
    AKShare data source - 免费开源的金融数据接口

    优势：
    - 完全免费，无需 token
    - 数据丰富：A股、港股、美股、期货、基金等
    - 实时数据、新闻、公告
    - 社区活跃，更新快

    与 Tushare 的分工：
    - Tushare: 历史数据、财务报表（需要积分）
    - AKShare: 实时数据、新闻公告（完全免费）

    文档：https://akshare.akfamily.xyz/
    """

    def __init__(self):
        logger.info("AKShare initialized (无需配置)")

    def get_realtime_quote(self, symbol: str) -> Dict[str, Any]:
        """
        获取实时行情

        Args:
            symbol: 股票代码 (e.g., "600519" for A股, "00700" for 港股)

        Returns:
            实时行情数据
        """
        try:
            # 判断市场
            if len(symbol) == 6 and symbol.isdigit():
                # A股
                if symbol.startswith(('60', '68')):
                    df = ak.stock_zh_a_spot_em()
                    result = df[df['代码'] == symbol]
                elif symbol.startswith(('00', '30')):
                    df = ak.stock_zh_a_spot_em()
                    result = df[df['代码'] == symbol]
                else:
                    return {}
            elif len(symbol) == 5:
                # 港股
                df = ak.stock_hk_spot_em()
                result = df[df['代码'] == symbol]
            else:
                return {}

            if result.empty:
                return {}

            return result.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error fetching realtime quote: {e}")
            return {}

    def get_stock_news(
        self,
        symbol: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取股票新闻

        Args:
            symbol: 股票代码（可选，如果为 None 则获取市场新闻）
            limit: 返回条数

        Returns:
            新闻列表
        """
        try:
            if symbol:
                # 个股新闻
                df = ak.stock_news_em(symbol=symbol)
            else:
                # 市场新闻
                df = ak.stock_news_em()

            if df.empty:
                return []

            return df.head(limit).to_dict('records')

        except Exception as e:
            logger.error(f"Error fetching stock news: {e}")
            return []

    def get_stock_announcements(
        self,
        symbol: str,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        获取公司公告

        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            公告列表
        """
        try:
            # 默认获取最近30天
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            df = ak.stock_notice_report(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )

            if df.empty:
                return []

            return df.to_dict('records')

        except Exception as e:
            logger.error(f"Error fetching announcements: {e}")
            return []

    def get_stock_hot_rank(self) -> List[Dict[str, Any]]:
        """
        获取股票热度排行

        Returns:
            热度排行榜
        """
        try:
            # 东方财富人气榜
            df = ak.stock_hot_rank_em()

            if df.empty:
                return []

            return df.to_dict('records')

        except Exception as e:
            logger.error(f"Error fetching hot rank: {e}")
            return []

    def get_stock_individual_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取个股基本信息

        Args:
            symbol: 股票代码

        Returns:
            个股信息
        """
        try:
            df = ak.stock_individual_info_em(symbol=symbol)

            if df.empty:
                return {}

            # 转换为字典格式
            info = {}
            for _, row in df.iterrows():
                info[row['item']] = row['value']

            return info

        except Exception as e:
            logger.error(f"Error fetching individual info: {e}")
            return {}

    def get_stock_concept(self, symbol: str) -> List[str]:
        """
        获取股票所属概念板块

        Args:
            symbol: 股票代码

        Returns:
            概念列表
        """
        try:
            df = ak.stock_board_concept_name_em()

            if df.empty:
                return []

            # 查找包含该股票的概念
            concepts = []
            for _, row in df.iterrows():
                # 获取概念成分股
                try:
                    concept_stocks = ak.stock_board_concept_cons_em(symbol=row['板块名称'])
                    if symbol in concept_stocks['代码'].values:
                        concepts.append(row['板块名称'])
                except:
                    continue

            return concepts

        except Exception as e:
            logger.error(f"Error fetching stock concepts: {e}")
            return []

    def get_stock_fund_flow(self, symbol: str) -> Dict[str, Any]:
        """
        获取资金流向

        Args:
            symbol: 股票代码

        Returns:
            资金流向数据
        """
        try:
            df = ak.stock_individual_fund_flow(stock=symbol, market="sh" if symbol.startswith('6') else "sz")

            if df.empty:
                return {}

            # 获取最新一天的数据
            latest = df.iloc[-1].to_dict()
            return latest

        except Exception as e:
            logger.error(f"Error fetching fund flow: {e}")
            return {}

    def get_stock_comments(self, symbol: str) -> List[Dict[str, Any]]:
        """
        获取千股千评

        Args:
            symbol: 股票代码

        Returns:
            评论列表
        """
        try:
            df = ak.stock_comment_em()

            if df.empty:
                return []

            # 筛选指定股票
            result = df[df['代码'] == symbol]

            if result.empty:
                return []

            return result.to_dict('records')

        except Exception as e:
            logger.error(f"Error fetching comments: {e}")
            return []

    def get_market_sentiment(self) -> Dict[str, Any]:
        """
        获取市场情绪指标

        Returns:
            市场情绪数据
        """
        try:
            # 涨跌停数据
            df_limit_up = ak.stock_em_zt_pool_em(date=datetime.now().strftime("%Y%m%d"))
            df_limit_down = ak.stock_em_dt_pool_em(date=datetime.now().strftime("%Y%m%d"))

            sentiment = {
                "limit_up_count": len(df_limit_up) if not df_limit_up.empty else 0,
                "limit_down_count": len(df_limit_down) if not df_limit_down.empty else 0,
                "sentiment_score": None,  # 可以根据涨跌停数量计算
            }

            # 计算情绪得分（简单算法）
            if sentiment["limit_up_count"] + sentiment["limit_down_count"] > 0:
                sentiment["sentiment_score"] = (
                    sentiment["limit_up_count"] - sentiment["limit_down_count"]
                ) / (sentiment["limit_up_count"] + sentiment["limit_down_count"])

            return sentiment

        except Exception as e:
            logger.error(f"Error fetching market sentiment: {e}")
            return {}

    def get_us_stock_realtime(self, symbol: str) -> Dict[str, Any]:
        """
        获取美股实时行情

        Args:
            symbol: 美股代码 (e.g., "AAPL", "TSLA")

        Returns:
            美股实时数据
        """
        try:
            df = ak.stock_us_spot_em()

            if df.empty:
                return {}

            result = df[df['代码'] == symbol]

            if result.empty:
                return {}

            return result.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error fetching US stock: {e}")
            return {}

    def normalize_symbol(self, symbol: str, market: str = "A") -> str:
        """
        标准化股票代码

        Args:
            symbol: 原始代码
            market: 市场类型 ("A", "HK", "US")

        Returns:
            标准化代码
        """
        symbol = symbol.strip().upper()

        if market == "A":
            # 去掉后缀
            if '.' in symbol:
                symbol = symbol.split('.')[0]
            # 确保是6位数字
            if symbol.isdigit() and len(symbol) == 6:
                return symbol

        elif market == "HK":
            # 港股代码标准化为5位
            if symbol.isdigit():
                return symbol.zfill(5)

        elif market == "US":
            # 美股保持原样
            return symbol

        return symbol


# 全局实例
akshare_api = AKShareDataSource()


# 便捷函数
def get_stock_realtime_data(symbol: str, market: str = "A") -> Dict[str, Any]:
    """
    快速获取股票实时数据

    Args:
        symbol: 股票代码
        market: 市场 ("A", "HK", "US")

    Returns:
        实时数据字典
    """
    normalized_symbol = akshare_api.normalize_symbol(symbol, market)

    if market == "US":
        return akshare_api.get_us_stock_realtime(normalized_symbol)
    else:
        return akshare_api.get_realtime_quote(normalized_symbol)


def get_stock_comprehensive_info(symbol: str) -> Dict[str, Any]:
    """
    获取股票综合信息（实时+新闻+公告）

    Args:
        symbol: 股票代码

    Returns:
        综合信息字典
    """
    return {
        "realtime": akshare_api.get_realtime_quote(symbol),
        "basic_info": akshare_api.get_stock_individual_info(symbol),
        "news": akshare_api.get_stock_news(symbol, limit=10),
        "announcements": akshare_api.get_stock_announcements(symbol),
        "concepts": akshare_api.get_stock_concept(symbol),
        "fund_flow": akshare_api.get_stock_fund_flow(symbol),
        "comments": akshare_api.get_stock_comments(symbol),
    }
