"""
FinanceDataReader - Financial Data Reader for Finance

한국 및 글로벌 금융 시장 데이터 조회 라이브러리

Examples:
    >>> import FinanceDataReader as fdr
    >>>
    >>> # 주가 데이터 조회
    >>> df = fdr.DataReader('005930', '2020-01-01', '2020-12-31')  # 삼성전자
    >>> df = fdr.DataReader('AAPL', '2020')  # Apple
    >>>
    >>> # 종목 목록 조회
    >>> df_krx = fdr.StockListing('KRX')
    >>> df_kospi = fdr.StockListing('KOSPI')
    >>>
    >>> # 스냅샷 데이터
    >>> df_index = fdr.SnapDataReader('KRX/INDEX/LIST')
"""

__version__ = '0.1.0'
__author__ = 'FinanceDataReader Implementation'
__license__ = 'MIT'

from .data import DataReader, StockListing
from .snap import SnapDataReader

__all__ = [
    'DataReader',
    'StockListing',
    'SnapDataReader',
    '__version__',
]
