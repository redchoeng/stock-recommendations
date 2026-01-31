"""네이버 금융 주가 데이터 조회"""

import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Optional
from ..utils import get_request, create_session, date_to_str_yahoo


# 네이버 금융 API
NAVER_FINANCE_API_URL = "https://fchart.stock.naver.com/sise.nhn"


def get_naver_data(
    stock_code: str,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    """
    네이버 금융에서 주가 데이터 조회

    Args:
        stock_code: 종목 코드 (6자리, 예: '005930')
        start: 시작일
        end: 종료일

    Returns:
        주가 데이터 DataFrame
        Columns: Date, Open, High, Low, Close, Volume
    """
    # 6자리 코드로 정규화
    stock_code = stock_code.zfill(6)

    try:
        # 네이버 금융 차트 API 사용
        params = {
            'symbol': stock_code,
            'requestType': 1,  # 일봉
            'startTime': start.strftime('%Y%m%d'),
            'endTime': end.strftime('%Y%m%d'),
            'timeframe': 'day'
        }

        session = create_session()
        response = get_request(
            NAVER_FINANCE_API_URL,
            params=params,
            session=session
        )

        # XML 파싱
        soup = BeautifulSoup(response.text, 'lxml')

        # 데이터 추출
        items = soup.find_all('item')

        if not items:
            print(f"No data found for {stock_code}")
            return pd.DataFrame()

        data_list = []
        for item in items:
            try:
                # item의 data 속성: 날짜|시가|고가|저가|종가|거래량
                data = item.get('data', '').split('|')

                if len(data) >= 6:
                    date_str = data[0]
                    open_price = float(data[1])
                    high_price = float(data[2])
                    low_price = float(data[3])
                    close_price = float(data[4])
                    volume = int(data[5])

                    # 날짜 파싱 (YYYYMMDD)
                    date = datetime.strptime(date_str, '%Y%m%d')

                    data_list.append({
                        'Date': date,
                        'Open': open_price,
                        'High': high_price,
                        'Low': low_price,
                        'Close': close_price,
                        'Volume': volume
                    })
            except (ValueError, IndexError) as e:
                # 파싱 실패한 항목은 스킵
                continue

        if not data_list:
            return pd.DataFrame()

        # DataFrame 생성
        df = pd.DataFrame(data_list)
        df = df.set_index('Date')
        df = df.sort_index()

        # 날짜 범위 필터링
        df = df[(df.index >= start) & (df.index <= end)]

        return df

    except Exception as e:
        print(f"Warning: Naver API failed for {stock_code} ({e})")
        return pd.DataFrame()


def get_naver_index_data(
    index_code: str,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    """
    네이버 금융에서 지수 데이터 조회

    Args:
        index_code: 지수 코드 (예: 'KS11', 'KQ11')
        start: 시작일
        end: 종료일

    Returns:
        지수 데이터 DataFrame
    """
    # 지수 코드 매핑
    index_map = {
        'KS11': 'KOSPI',
        'KQ11': 'KOSDAQ',
        'KS50': 'KRX100',
        'KS100': 'KOSPI100',
    }

    # 지수는 일반 종목과 동일한 API 사용
    return get_naver_data(index_code, start, end)
