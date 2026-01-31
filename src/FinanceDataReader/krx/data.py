"""KRX 주가 데이터 조회"""

import pandas as pd
import json
from datetime import datetime
from typing import Optional
from ..utils import get_request, post_request, create_session, date_to_str_krx, get_date_chunks


# KRX API 엔드포인트
KRX_STOCK_URL = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
KRX_OTP_URL = "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd"


def get_krx_price_otp(
    stock_code: str,
    start_date: str,
    end_date: str
) -> str:
    """
    KRX 주가 조회용 OTP 발급

    Args:
        stock_code: 종목 코드 (6자리)
        start_date: 시작일 (YYYYMMDD)
        end_date: 종료일 (YYYYMMDD)

    Returns:
        OTP 문자열
    """
    params = {
        'locale': 'ko_KR',
        'isuCd': stock_code,
        'strtDd': start_date,
        'endDd': end_date,
        'share': '1',
        'money': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT01701'
    }

    session = create_session()
    response = get_request(KRX_OTP_URL, params=params, session=session)

    return response.text


def fetch_krx_stock_data(
    stock_code: str,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    """
    KRX에서 주가 데이터 조회

    Args:
        stock_code: 종목 코드 (6자리, 예: '005930')
        start: 시작일
        end: 종료일

    Returns:
        주가 데이터 DataFrame
        Columns: Date, Open, High, Low, Close, Volume, Change 등
    """
    # 6자리 코드로 정규화
    stock_code = stock_code.zfill(6)

    # 날짜를 KRX 형식으로 변환
    start_str = date_to_str_krx(start)
    end_str = date_to_str_krx(end)

    try:
        # Step 1: OTP 발급
        otp = get_krx_price_otp(stock_code, start_str, end_str)

        # Step 2: OTP로 데이터 요청
        data = {
            'code': otp,
            'isuCd': stock_code,
            'strtDd': start_str,
            'endDd': end_str,
            'share': '1',
            'money': '1',
            'csvxls_isNo': 'false'
        }

        session = create_session()
        headers = {
            'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
            'User-Agent': 'Mozilla/5.0'
        }

        response = post_request(
            KRX_STOCK_URL,
            data=data,
            headers=headers,
            session=session
        )

        # JSON 파싱
        result = json.loads(response.text)

        # DataFrame 변환
        if 'output' in result:
            df = pd.DataFrame(result['output'])
        elif 'OutBlock_1' in result:
            df = pd.DataFrame(result['OutBlock_1'])
        else:
            # 응답에서 리스트 찾기
            for key, value in result.items():
                if isinstance(value, list) and len(value) > 0:
                    df = pd.DataFrame(value)
                    break
            else:
                raise ValueError(f"No data found in response for {stock_code}")

        if df.empty:
            return pd.DataFrame()

        # 컬럼명 정규화
        column_map = {
            'TRD_DD': 'Date',
            'TDD_CLSPRC': 'Close',
            'TDD_OPNPRC': 'Open',
            'TDD_HGPRC': 'High',
            'TDD_LWPRC': 'Low',
            'ACC_TRDVOL': 'Volume',
            'ACC_TRDVAL': 'Amount',
            'FLUC_RT': 'Change',
            'CMPPREVDD_PRC': 'ChgAmount',
        }

        df = df.rename(columns=column_map)

        # Date 컬럼 처리
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d', errors='coerce')
            df = df.set_index('Date')

        # 숫자형 컬럼 변환
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Amount', 'Change']
        for col in numeric_columns:
            if col in df.columns:
                # 쉼표 제거 후 숫자 변환
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)

        # OHLCV 순서로 정렬
        ohlcv_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [col for col in ohlcv_cols if col in df.columns]
        other_cols = [col for col in df.columns if col not in ohlcv_cols]

        df = df[available_cols + other_cols]

        # 날짜순 정렬
        df = df.sort_index()

        return df

    except Exception as e:
        print(f"Warning: KRX API failed for {stock_code} ({e})")
        return pd.DataFrame()


def get_krx_data(
    stock_code: str,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    """
    KRX 데이터 조회 (청크 단위로 분할하여 조회)

    KRX는 한 번에 2년치 데이터만 조회 가능하므로 청크로 분할

    Args:
        stock_code: 종목 코드
        start: 시작일
        end: 종료일

    Returns:
        전체 기간 주가 데이터 DataFrame
    """
    # 2년 단위로 청크 분할
    chunks = get_date_chunks(start, end, chunk_years=2)

    all_data = []

    for chunk_start, chunk_end in chunks:
        df_chunk = fetch_krx_stock_data(stock_code, chunk_start, chunk_end)

        if not df_chunk.empty:
            all_data.append(df_chunk)

    if not all_data:
        return pd.DataFrame()

    # 모든 청크 병합
    df = pd.concat(all_data)

    # 중복 제거 (날짜 기준)
    df = df[~df.index.duplicated(keep='first')]

    # 날짜순 정렬
    df = df.sort_index()

    return df
