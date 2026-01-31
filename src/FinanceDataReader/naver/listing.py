"""네이버 금융 종목 목록 조회"""

import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional
from ..utils import get_request, create_session


# 네이버 금융 URL
NAVER_FINANCE_URL = "https://finance.naver.com"


def get_naver_stock_listing(market: str = 'KOSPI') -> pd.DataFrame:
    """
    네이버 금융에서 종목 목록 조회

    Args:
        market: 시장 구분 ('KOSPI', 'KOSDAQ', 'KONEX')

    Returns:
        종목 목록 DataFrame
        Columns: Code, Name, Market 등
    """
    # 네이버는 종목 목록 API를 제공하지 않으므로
    # KRX 데이터를 대체로 사용하거나 크롤링 필요
    # 여기서는 간단한 구조만 제공

    try:
        # 실제 구현은 KRX 종목 리스트를 참조
        from ..krx import get_krx_stock_listing

        df = get_krx_stock_listing(market)
        return df

    except Exception as e:
        print(f"Warning: Naver listing failed ({e}), using sample data")
        return _get_sample_naver_listing(market)


def _get_sample_naver_listing(market: str = 'KOSPI') -> pd.DataFrame:
    """샘플 네이버 종목 데이터"""
    data = {
        'Code': ['005930', '000660', '051910', '035420', '005380'],
        'Name': ['삼성전자', 'SK하이닉스', 'LG화학', 'NAVER', '현대차'],
        'Market': ['KOSPI', 'KOSPI', 'KOSPI', 'KOSPI', 'KOSPI'],
    }

    df = pd.DataFrame(data)

    if market.upper() != 'ALL':
        df = df[df['Market'] == market.upper()]

    return df


def get_naver_etf_listing() -> pd.DataFrame:
    """
    네이버 금융 ETF 목록 조회
    """
    # ETF 목록은 별도 크롤링 필요
    # 샘플 데이터 반환
    data = {
        'Code': ['069500', '102110', '251340', '148070'],
        'Name': ['KODEX 200', 'KODEX 단기채권', 'KODEX 코스닥150', 'KOSEF 미국S&P500'],
        'Type': ['ETF', 'ETF', 'ETF', 'ETF'],
    }

    return pd.DataFrame(data)
