"""스냅샷 데이터 리더 (비시계열 데이터)"""

import pandas as pd
from typing import Optional

from .krx import get_krx_stock_listing


def SnapDataReader(path: str) -> pd.DataFrame:
    """
    스냅샷 데이터 조회 (비시계열 데이터)

    Args:
        path: 데이터 경로
            - 'KRX/INDEX/LIST': KRX 인덱스 목록
            - 'KRX/STOCK/LIST': KRX 주식 목록
            - 'NAVER/FINSTATE/종목코드': 네이버 재무제표
            - 'NAVER/SECTOR': 업종별 현재가

    Returns:
        스냅샷 데이터 DataFrame

    Examples:
        >>> import FinanceDataReader as fdr
        >>> df = fdr.SnapDataReader('KRX/INDEX/LIST')  # KRX 인덱스 목록
        >>> df = fdr.SnapDataReader('NAVER/FINSTATE/005930')  # 삼성전자 재무제표
    """
    path = path.upper()
    parts = path.split('/')

    if len(parts) < 2:
        raise ValueError(f"Invalid path format: {path}")

    source = parts[0]

    # KRX 데이터
    if source == 'KRX':
        return _get_krx_snap_data(parts)

    # NAVER 데이터
    elif source == 'NAVER':
        return _get_naver_snap_data(parts)

    else:
        raise ValueError(f"Unknown snap data source: {source}")


def _get_krx_snap_data(parts: list) -> pd.DataFrame:
    """KRX 스냅샷 데이터 조회"""
    if len(parts) < 3:
        raise ValueError("KRX snap data requires format: KRX/TYPE/SUBTYPE")

    data_type = parts[1]
    subtype = parts[2]

    # 인덱스 목록
    if data_type == 'INDEX' and subtype == 'LIST':
        return _get_krx_index_list()

    # 주식 목록
    elif data_type == 'STOCK' and subtype == 'LIST':
        market = parts[3] if len(parts) > 3 else 'ALL'
        return get_krx_stock_listing(market)

    else:
        raise ValueError(f"Unknown KRX snap data type: {data_type}/{subtype}")


def _get_krx_index_list() -> pd.DataFrame:
    """KRX 인덱스 목록"""
    data = {
        'Code': ['KS11', 'KQ11', 'KS50', 'KS100', 'KRX100'],
        'Name': ['KOSPI', 'KOSDAQ', 'KOSPI50', 'KOSPI100', 'KRX100'],
        'Market': ['KOSPI', 'KOSDAQ', 'KOSPI', 'KOSPI', 'KRX'],
        'Type': ['Index', 'Index', 'Index', 'Index', 'Index'],
    }

    return pd.DataFrame(data)


def _get_naver_snap_data(parts: list) -> pd.DataFrame:
    """네이버 스냅샷 데이터 조회"""
    if len(parts) < 2:
        raise ValueError("NAVER snap data requires format: NAVER/TYPE/...")

    data_type = parts[1]

    # 재무제표
    if data_type == 'FINSTATE':
        if len(parts) < 3:
            raise ValueError("NAVER/FINSTATE requires stock code")
        stock_code = parts[2]
        return _get_naver_financial_statement(stock_code)

    # 업종별 현재가
    elif data_type == 'SECTOR':
        return _get_naver_sector_data()

    else:
        raise ValueError(f"Unknown NAVER snap data type: {data_type}")


def _get_naver_financial_statement(stock_code: str) -> pd.DataFrame:
    """
    네이버 금융 재무제표 조회

    실제 구현은 네이버 금융 페이지 크롤링 필요
    여기서는 샘플 데이터 반환
    """
    print(f"Warning: Financial statement for {stock_code} - using sample data")

    # 샘플 재무제표 데이터
    data = {
        'Account': ['매출액', '영업이익', '당기순이익', '자산총계', '부채총계', '자본총계'],
        '2023': [100000, 15000, 12000, 80000, 30000, 50000],
        '2022': [95000, 14000, 11000, 75000, 28000, 47000],
        '2021': [90000, 13000, 10000, 70000, 26000, 44000],
    }

    return pd.DataFrame(data)


def _get_naver_sector_data() -> pd.DataFrame:
    """
    네이버 금융 업종별 현재가

    실제 구현은 네이버 금융 페이지 크롤링 필요
    """
    print("Warning: Sector data - using sample data")

    data = {
        'Sector': ['전기전자', '화학', '운수장비', '금융', '서비스업'],
        'Change': [1.5, -0.3, 2.1, 0.8, 1.2],
        'Volume': [1000000, 500000, 750000, 300000, 450000],
    }

    return pd.DataFrame(data)
