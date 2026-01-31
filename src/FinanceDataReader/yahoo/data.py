"""Yahoo Finance 데이터 조회"""

import pandas as pd
from datetime import datetime
import json
from typing import Optional
from ..utils import get_request, create_session


# Yahoo Finance API
YAHOO_FINANCE_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
YAHOO_FINANCE_V7_URL = "https://query1.finance.yahoo.com/v7/finance/download/{symbol}"


def get_yahoo_data(
    symbol: str,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    """
    Yahoo Finance에서 주가 데이터 조회

    Args:
        symbol: 티커 심볼 (예: 'AAPL', '005930.KS')
        start: 시작일
        end: 종료일

    Returns:
        주가 데이터 DataFrame
        Columns: Date, Open, High, Low, Close, Volume, Adj Close
    """
    try:
        # Unix timestamp 변환
        period1 = int(start.timestamp())
        period2 = int(end.timestamp())

        # Yahoo Finance API 호출
        params = {
            'period1': period1,
            'period2': period2,
            'interval': '1d',
            'events': 'history',
            'includeAdjustedClose': 'true'
        }

        session = create_session()
        url = YAHOO_FINANCE_V7_URL.format(symbol=symbol)

        response = get_request(url, params=params, session=session)

        # CSV 파싱
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))

        if df.empty:
            return pd.DataFrame()

        # Date 컬럼을 인덱스로
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date')

        # 컬럼명 정규화
        column_map = {
            'Open': 'Open',
            'High': 'High',
            'Low': 'Low',
            'Close': 'Close',
            'Adj Close': 'Adj Close',
            'Volume': 'Volume'
        }

        df = df.rename(columns=column_map)

        # NaN 제거
        df = df.dropna()

        # 날짜순 정렬
        df = df.sort_index()

        return df

    except Exception as e:
        print(f"Warning: Yahoo Finance API failed for {symbol} ({e})")

        # 대체 방법: Chart API 사용
        try:
            return _get_yahoo_data_chart_api(symbol, start, end)
        except Exception as e2:
            print(f"Warning: Yahoo Chart API also failed ({e2})")
            return pd.DataFrame()


def _get_yahoo_data_chart_api(
    symbol: str,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    """
    Yahoo Finance Chart API 사용 (대체 방법)

    Args:
        symbol: 티커 심볼
        start: 시작일
        end: 종료일

    Returns:
        주가 데이터 DataFrame
    """
    period1 = int(start.timestamp())
    period2 = int(end.timestamp())

    params = {
        'period1': period1,
        'period2': period2,
        'interval': '1d',
        'includePrePost': 'false',
    }

    session = create_session()
    url = YAHOO_FINANCE_API_URL.format(symbol=symbol)

    response = get_request(url, params=params, session=session)

    data = json.loads(response.text)

    # 데이터 추출
    chart = data['chart']['result'][0]

    timestamps = chart['timestamp']
    quote = chart['indicators']['quote'][0]

    # Adjusted Close (있는 경우)
    adj_close = None
    if 'adjclose' in chart['indicators']:
        adj_close = chart['indicators']['adjclose'][0]['adjclose']

    # DataFrame 생성
    df_data = {
        'Date': [datetime.fromtimestamp(ts) for ts in timestamps],
        'Open': quote['open'],
        'High': quote['high'],
        'Low': quote['low'],
        'Close': quote['close'],
        'Volume': quote['volume'],
    }

    if adj_close:
        df_data['Adj Close'] = adj_close

    df = pd.DataFrame(df_data)
    df = df.set_index('Date')
    df = df.dropna()
    df = df.sort_index()

    return df


def normalize_yahoo_symbol(symbol: str, market: Optional[str] = None) -> str:
    """
    Yahoo Finance 심볼 형식으로 정규화

    Args:
        symbol: 종목 코드
        market: 시장 구분 ('KS', 'KQ', 'US' 등)

    Returns:
        정규화된 심볼

    Examples:
        >>> normalize_yahoo_symbol('005930', 'KS')
        '005930.KS'
        >>> normalize_yahoo_symbol('AAPL')
        'AAPL'
    """
    # 이미 형식이 올바른 경우
    if '.' in symbol or not market:
        return symbol

    # 한국 주식 코드 변환
    if market == 'KS' or market == 'KOSPI':
        return f"{symbol.zfill(6)}.KS"
    elif market == 'KQ' or market == 'KOSDAQ':
        return f"{symbol.zfill(6)}.KQ"

    return symbol
