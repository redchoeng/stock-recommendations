"""메인 데이터 리더 함수"""

import pandas as pd
from datetime import datetime
from typing import Optional, Union

from .utils import get_default_dates, parse_date
from .krx import get_krx_data, get_krx_stock_listing
from .naver import get_naver_data
from .yahoo import get_yahoo_data, normalize_yahoo_symbol
from .crypto import get_crypto_data, parse_crypto_symbol
from .fred import get_fred_data


def DataReader(
    symbol: str,
    start: Optional[Union[str, datetime]] = None,
    end: Optional[Union[str, datetime]] = None,
    data_source: Optional[str] = None
) -> pd.DataFrame:
    """
    금융 데이터 조회 (통합 인터페이스)

    Args:
        symbol: 종목 코드 또는 티커
            - 한국 주식: '005930', '000660' (6자리)
            - 미국 주식: 'AAPL', 'TSLA'
            - 지수: 'KS11'(KOSPI), 'KQ11'(KOSDAQ), 'DJI', 'IXIC'
            - 환율: 'USD/KRW', 'EUR/USD'
            - 암호화폐: 'BTC/USD', 'ETH/KRW'
            - FRED: 'FRED:GDP', 'FRED:UNRATE'
            - 소스 지정: 'KRX:005930', 'NAVER:005930', 'YAHOO:AAPL'

        start: 시작일 (YYYY, YYYY-MM-DD, datetime)
        end: 종료일 (YYYY, YYYY-MM-DD, datetime)
        data_source: 데이터 소스 ('KRX', 'NAVER', 'YAHOO', 'FRED', 'CRYPTO')
            None이면 자동 선택

    Returns:
        주가/지수 데이터 DataFrame
        Columns: Open, High, Low, Close, Volume (데이터 소스별로 다를 수 있음)

    Examples:
        >>> import FinanceDataReader as fdr
        >>> df = fdr.DataReader('005930', '2020-01-01', '2020-12-31')  # 삼성전자
        >>> df = fdr.DataReader('AAPL', '2020')  # Apple
        >>> df = fdr.DataReader('BTC/USD', '2020-01-01')  # 비트코인
        >>> df = fdr.DataReader('FRED:GDP', '2010', '2020')  # GDP 데이터
    """
    # 날짜 처리
    if isinstance(start, str):
        start_dt, end_dt = get_default_dates(start, end)
    elif isinstance(start, datetime):
        start_dt = start
        end_dt = end if isinstance(end, datetime) else datetime.now()
    else:
        # start가 None인 경우
        start_dt, end_dt = get_default_dates()

    # 소스 접두사 파싱
    if ':' in symbol:
        parts = symbol.split(':', 1)
        data_source = parts[0].upper()
        symbol = parts[1]

    # 데이터 소스 자동 감지
    if data_source is None:
        data_source = _detect_data_source(symbol)

    # 데이터 소스별 라우팅
    data_source = data_source.upper()

    if data_source == 'KRX':
        return get_krx_data(symbol, start_dt, end_dt)

    elif data_source == 'NAVER':
        return get_naver_data(symbol, start_dt, end_dt)

    elif data_source == 'YAHOO':
        return get_yahoo_data(symbol, start_dt, end_dt)

    elif data_source == 'FRED':
        return get_fred_data(symbol, start_dt, end_dt)

    elif data_source == 'CRYPTO':
        coin_symbol, currency = parse_crypto_symbol(symbol)
        return get_crypto_data(coin_symbol, start_dt, end_dt, currency.lower())

    else:
        raise ValueError(f"Unknown data source: {data_source}")


def StockListing(market: str = 'KRX') -> pd.DataFrame:
    """
    거래소 종목 목록 조회

    Args:
        market: 시장 코드
            - 'KRX': 전체 (KOSPI + KOSDAQ + KONEX)
            - 'KOSPI': 코스피
            - 'KOSDAQ': 코스닥
            - 'KONEX': 코넥스
            - 'NASDAQ': 나스닥
            - 'NYSE': 뉴욕증권거래소
            - 'S&P500': S&P 500 구성 종목

    Returns:
        종목 목록 DataFrame
        Columns: Code, Name, Market, Sector 등

    Examples:
        >>> import FinanceDataReader as fdr
        >>> df_krx = fdr.StockListing('KRX')
        >>> df_kospi = fdr.StockListing('KOSPI')
    """
    market = market.upper()

    # 한국 시장
    if market in ['KRX', 'KOSPI', 'KOSDAQ', 'KONEX']:
        return get_krx_stock_listing(market)

    # 해외 시장 (Yahoo Finance 또는 별도 구현 필요)
    elif market in ['NASDAQ', 'NYSE', 'S&P500', 'SP500']:
        # 실제 구현은 별도 크롤링이나 API 필요
        # 여기서는 샘플 데이터 반환
        return _get_sample_global_listing(market)

    else:
        raise ValueError(f"Unknown market: {market}")


def _detect_data_source(symbol: str) -> str:
    """
    심볼을 보고 데이터 소스 자동 감지

    Args:
        symbol: 종목 코드 또는 티커

    Returns:
        데이터 소스 이름
    """
    symbol_upper = symbol.upper()

    # FRED 데이터
    if symbol_upper.startswith('FRED:'):
        return 'FRED'

    # 암호화폐 (BTC/USD, ETH/KRW 형식)
    if '/' in symbol_upper:
        # 환율도 포함될 수 있음
        parts = symbol_upper.split('/')
        crypto_symbols = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'DOGE', 'SOL', 'DOT', 'MATIC', 'LTC']
        if parts[0] in crypto_symbols:
            return 'CRYPTO'

    # 한국 주식 (6자리 숫자)
    if symbol.isdigit() and len(symbol) == 6:
        # 기본값은 NAVER (빠른 접근)
        return 'NAVER'

    # 한국 지수
    if symbol_upper in ['KS11', 'KQ11', 'KS50', 'KS100']:
        return 'NAVER'

    # 미국 주식 및 기타
    # AAPL, TSLA 등 알파벳 티커
    return 'YAHOO'


def _get_sample_global_listing(market: str) -> pd.DataFrame:
    """해외 시장 샘플 종목 리스트"""
    if market == 'NASDAQ' or market == 'NASDAQNM':
        data = {
            'Code': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
            'Name': ['Apple Inc.', 'Microsoft Corp.', 'Alphabet Inc.', 'Amazon.com Inc.', 'Tesla Inc.'],
            'Market': ['NASDAQ'] * 5,
        }
    elif market == 'NYSE':
        data = {
            'Code': ['JPM', 'V', 'JNJ', 'WMT', 'PG'],
            'Name': ['JPMorgan Chase', 'Visa Inc.', 'Johnson & Johnson', 'Walmart Inc.', 'Procter & Gamble'],
            'Market': ['NYSE'] * 5,
        }
    elif market in ['S&P500', 'SP500']:
        data = {
            'Code': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'JPM', 'V', 'JNJ', 'WMT', 'PG'],
            'Name': ['Apple', 'Microsoft', 'Alphabet', 'Amazon', 'Tesla',
                    'JPMorgan', 'Visa', 'Johnson & Johnson', 'Walmart', 'Procter & Gamble'],
            'Market': ['S&P500'] * 10,
        }
    else:
        data = {'Code': [], 'Name': [], 'Market': []}

    return pd.DataFrame(data)
