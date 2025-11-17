"""Tushare data source tool for Chinese stock market data."""

import os
import tushare as ts
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from loguru import logger


class TushareDataSource:
    """
    Tushare data source for Chinese stock market.

    API Documentation: https://tushare.pro/document/2
    """

    def __init__(self):
        token = os.getenv("TUSHARE_TOKEN")
        if not token:
            logger.warning("TUSHARE_TOKEN not set. Some features will be unavailable.")
            self.pro = None
        else:
            ts.set_token(token)
            self.pro = ts.pro_api()
            logger.info("Tushare API initialized")

    def get_stock_basic(self, ts_code: str = None) -> Dict[str, Any]:
        """
        获取股票基本信息

        Args:
            ts_code: 股票代码 (e.g., "600519.SH")

        Returns:
            股票基本信息
        """
        if not self.pro:
            logger.error("Tushare API not initialized")
            return {}

        try:
            if ts_code:
                df = self.pro.stock_basic(ts_code=ts_code)
            else:
                df = self.pro.stock_basic(exchange='', list_status='L')

            if df.empty:
                return {}

            return df.iloc[0].to_dict() if ts_code else df.to_dict('records')

        except Exception as e:
            logger.error(f"Error fetching stock basic info: {e}")
            return {}

    def get_daily_price(
        self,
        ts_code: str,
        start_date: str = None,
        end_date: str = None,
    ) -> List[Dict[str, Any]]:
        """
        获取日线行情

        Args:
            ts_code: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            日线数据列表
        """
        if not self.pro:
            return []

        try:
            # 默认获取最近30天
            if not end_date:
                end_date = datetime.now().strftime("%Y%m%d")
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )

            return df.to_dict('records') if not df.empty else []

        except Exception as e:
            logger.error(f"Error fetching daily price: {e}")
            return []

    def get_income_statement(
        self,
        ts_code: str,
        period: str = None,
    ) -> Dict[str, Any]:
        """
        获取利润表

        Args:
            ts_code: 股票代码
            period: 报告期 (YYYYMMDD), 如果为None则获取最新

        Returns:
            利润表数据
        """
        if not self.pro:
            return {}

        try:
            df = self.pro.income(ts_code=ts_code, period=period)

            if df.empty:
                return {}

            return df.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error fetching income statement: {e}")
            return {}

    def get_balance_sheet(
        self,
        ts_code: str,
        period: str = None,
    ) -> Dict[str, Any]:
        """
        获取资产负债表

        Args:
            ts_code: 股票代码
            period: 报告期

        Returns:
            资产负债表数据
        """
        if not self.pro:
            return {}

        try:
            df = self.pro.balancesheet(ts_code=ts_code, period=period)

            if df.empty:
                return {}

            return df.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error fetching balance sheet: {e}")
            return {}

    def get_cashflow_statement(
        self,
        ts_code: str,
        period: str = None,
    ) -> Dict[str, Any]:
        """
        获取现金流量表

        Args:
            ts_code: 股票代码
            period: 报告期

        Returns:
            现金流量表数据
        """
        if not self.pro:
            return {}

        try:
            df = self.pro.cashflow(ts_code=ts_code, period=period)

            if df.empty:
                return {}

            return df.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error fetching cashflow statement: {e}")
            return {}

    def get_financial_indicators(
        self,
        ts_code: str,
        period: str = None,
    ) -> Dict[str, Any]:
        """
        获取财务指标数据

        Args:
            ts_code: 股票代码
            period: 报告期

        Returns:
            财务指标数据 (ROE, ROA, 毛利率等)
        """
        if not self.pro:
            return {}

        try:
            df = self.pro.fina_indicator(ts_code=ts_code, period=period)

            if df.empty:
                return {}

            return df.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error fetching financial indicators: {e}")
            return {}

    def get_company_info(self, ts_code: str) -> Dict[str, Any]:
        """
        获取上市公司基本信息

        Args:
            ts_code: 股票代码

        Returns:
            公司基本信息
        """
        if not self.pro:
            return {}

        try:
            df = self.pro.stock_company(ts_code=ts_code)

            if df.empty:
                return {}

            return df.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error fetching company info: {e}")
            return {}

    def get_disclosure_date(self, ts_code: str) -> List[Dict[str, Any]]:
        """
        获取财报披露日期

        Args:
            ts_code: 股票代码

        Returns:
            披露日期列表
        """
        if not self.pro:
            return []

        try:
            df = self.pro.disclosure_date(ts_code=ts_code)
            return df.to_dict('records') if not df.empty else []

        except Exception as e:
            logger.error(f"Error fetching disclosure dates: {e}")
            return []

    def normalize_ticker(self, ticker: str) -> str:
        """
        标准化股票代码为 Tushare 格式

        Args:
            ticker: 原始代码 (e.g., "600519" or "000001")

        Returns:
            Tushare格式代码 (e.g., "600519.SH" or "000001.SZ")
        """
        ticker = ticker.strip()

        # 如果已经是标准格式，直接返回
        if '.' in ticker:
            return ticker.upper()

        # 6位数字代码
        if len(ticker) == 6 and ticker.isdigit():
            # 60/68开头 = 上海主板
            if ticker.startswith(('60', '68')):
                return f"{ticker}.SH"
            # 00/30开头 = 深圳
            elif ticker.startswith(('00', '30')):
                return f"{ticker}.SZ"
            # 科创板
            elif ticker.startswith('688'):
                return f"{ticker}.SH"
            # 创业板
            elif ticker.startswith('300'):
                return f"{ticker}.SZ"

        return ticker


# 全局实例
tushare_api = TushareDataSource()


# 便捷函数
def get_stock_info(ticker: str) -> Dict[str, Any]:
    """快速获取股票信息"""
    ts_code = tushare_api.normalize_ticker(ticker)

    basic = tushare_api.get_stock_basic(ts_code)
    company = tushare_api.get_company_info(ts_code)
    indicators = tushare_api.get_financial_indicators(ts_code)

    return {
        "basic": basic,
        "company": company,
        "indicators": indicators,
    }


def get_latest_financials(ticker: str) -> Dict[str, Any]:
    """获取最新财务数据"""
    ts_code = tushare_api.normalize_ticker(ticker)

    return {
        "income": tushare_api.get_income_statement(ts_code),
        "balance": tushare_api.get_balance_sheet(ts_code),
        "cashflow": tushare_api.get_cashflow_statement(ts_code),
        "indicators": tushare_api.get_financial_indicators(ts_code),
    }
