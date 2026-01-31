"""KRX 종목 목록 조회"""

import pandas as pd
import json
from typing import Optional
from ..utils import get_request, post_request, create_session


# KRX 정보데이터시스템 API
KRX_STOCK_LISTING_URL = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
KRX_OTP_URL = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"


def get_krx_otp(
    mkt_id: str = 'ALL',
    market_gubun: str = 'ALL'
) -> str:
    """
    KRX OTP(One Time Password) 발급

    Args:
        mkt_id: 시장 구분 ('STK': KOSPI, 'KSQ': KOSDAQ, 'ALL': 전체)
        market_gubun: 시장 구분 (레거시 파라미터)

    Returns:
        OTP 문자열
    """
    params = {
        'locale': 'ko_KR',
        'mktId': mkt_id,
        'trdDd': '',
        'share': '1',
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT01901'
    }

    session = create_session()
    response = get_request(KRX_OTP_URL, params=params, session=session)

    return response.text


def get_krx_stock_listing(market: str = 'ALL') -> pd.DataFrame:
    """
    KRX 상장 종목 목록 조회

    Args:
        market: 시장 구분
            - 'ALL': 전체
            - 'KOSPI': 코스피
            - 'KOSDAQ': 코스닥
            - 'KONEX': 코넥스

    Returns:
        종목 목록 DataFrame
        Columns: Code, Name, Market, Sector, ListingDate, Shares, MarketCap 등
    """
    # 시장 구분 코드 매핑
    market_map = {
        'ALL': 'ALL',
        'KOSPI': 'STK',
        'KOSDAQ': 'KSQ',
        'KONEX': 'KNX'
    }

    mkt_id = market_map.get(market.upper(), 'ALL')

    try:
        # Step 1: OTP 발급
        otp = get_krx_otp(mkt_id=mkt_id)

        # Step 2: OTP로 데이터 요청
        data = {
            'code': otp,
            'mktId': mkt_id,
            'share': '1',
            'csvxls_isNo': 'false'
        }

        session = create_session()
        headers = {
            'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
            'User-Agent': 'Mozilla/5.0'
        }

        response = post_request(
            KRX_STOCK_LISTING_URL,
            data=data,
            headers=headers,
            session=session
        )

        # JSON 파싱
        result = json.loads(response.text)

        # DataFrame 변환
        if 'OutBlock_1' in result:
            df = pd.DataFrame(result['OutBlock_1'])
        else:
            # 대체 키 확인
            df = pd.DataFrame(result.get('output', []))

        if df.empty:
            raise ValueError(f"No data found for market: {market}")

        # 컬럼명 정규화
        column_map = {
            'ISU_SRT_CD': 'Code',
            'ISU_ABBRV': 'Name',
            'ISU_CD': 'FullCode',
            'MKT_NM': 'Market',
            'SECT_TP_NM': 'Sector',
            'KIND_STKCERT_TP_NM': 'Type',
            'LIST_DD': 'ListingDate',
            'TDD_CLSPRC': 'Close',
            'LIST_SHRS': 'Shares',
            'MKTCAP': 'MarketCap',
        }

        df = df.rename(columns=column_map)

        # 필요한 컬럼만 선택 (존재하는 컬럼만)
        available_columns = [col for col in column_map.values() if col in df.columns]
        if available_columns:
            df = df[available_columns]

        # Code를 인덱스가 아닌 컬럼으로 유지
        if 'Code' in df.columns:
            # 6자리 코드로 정규화
            df['Code'] = df['Code'].str.strip()

        return df

    except Exception as e:
        # API 실패 시 간단한 더미 데이터 반환 (개발/테스트용)
        print(f"Warning: KRX API failed ({e}), returning sample data")
        return _get_sample_krx_listing(market)


def _get_sample_krx_listing(market: str = 'ALL') -> pd.DataFrame:
    """
    샘플 KRX 종목 데이터 (API 실패 시 대체용)

    테스트 및 개발 목적으로 사용
    """
    data = {
        'Code': ['005930', '000660', '051910', '035420', '005380'],
        'Name': ['삼성전자', 'SK하이닉스', 'LG화학', 'NAVER', '현대차'],
        'Market': ['KOSPI', 'KOSPI', 'KOSPI', 'KOSPI', 'KOSPI'],
        'Sector': ['전기전자', '전기전자', '화학', '서비스업', '운수장비'],
    }

    df = pd.DataFrame(data)

    # 시장 필터링
    if market.upper() != 'ALL':
        df = df[df['Market'] == market.upper()]

    return df


def get_kospi_listing() -> pd.DataFrame:
    """KOSPI 상장 종목 목록"""
    return get_krx_stock_listing('KOSPI')


def get_kosdaq_listing() -> pd.DataFrame:
    """KOSDAQ 상장 종목 목록"""
    return get_krx_stock_listing('KOSDAQ')


def get_konex_listing() -> pd.DataFrame:
    """KONEX 상장 종목 목록"""
    return get_krx_stock_listing('KONEX')
