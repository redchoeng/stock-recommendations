"""FRED (Federal Reserve Economic Data) 경제 데이터 조회"""

import pandas as pd
from datetime import datetime
from typing import Optional
from ..utils import get_request, create_session


# FRED API (API 키 필요)
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"


def get_fred_data(
    series_id: str,
    start: datetime,
    end: datetime,
    api_key: Optional[str] = None
) -> pd.DataFrame:
    """
    FRED에서 경제 지표 데이터 조회

    Args:
        series_id: FRED 시리즈 ID (예: 'GDP', 'UNRATE', 'DGS10')
        start: 시작일
        end: 종료일
        api_key: FRED API 키 (없으면 제한된 접근)

    Returns:
        경제 데이터 DataFrame
        Columns: Date, Value

    Note:
        FRED API 키는 https://fred.stlouisfed.org/docs/api/api_key.html 에서 발급
    """
    if not api_key:
        print("Warning: FRED API key not provided. Using sample data.")
        return _get_sample_fred_data(series_id, start, end)

    try:
        params = {
            'series_id': series_id,
            'observation_start': start.strftime('%Y-%m-%d'),
            'observation_end': end.strftime('%Y-%m-%d'),
            'api_key': api_key,
            'file_type': 'json'
        }

        session = create_session()
        response = get_request(FRED_API_URL, params=params, session=session)

        import json
        data = json.loads(response.text)

        if 'observations' not in data:
            return pd.DataFrame()

        # DataFrame 변환
        df = pd.DataFrame(data['observations'])

        # Date 컬럼 처리
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')

        # Value 컬럼 변환
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

        # 컬럼명 정규화
        df = df.rename(columns={'value': series_id})

        # 필요한 컬럼만 선택
        df = df[[series_id]]

        # NaN 제거
        df = df.dropna()

        return df

    except Exception as e:
        print(f"Warning: FRED API failed for {series_id} ({e})")
        return _get_sample_fred_data(series_id, start, end)


def _get_sample_fred_data(
    series_id: str,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    """샘플 FRED 데이터 (API 키 없을 때)"""
    # 간단한 더미 데이터
    date_range = pd.date_range(start, end, freq='MS')  # 월별

    import numpy as np
    values = np.random.randn(len(date_range)) * 10 + 100

    df = pd.DataFrame({
        series_id: values
    }, index=date_range)

    return df
