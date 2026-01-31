"""암호화폐 데이터 조회"""

import pandas as pd
from datetime import datetime
from typing import Optional
from ..utils import get_request, create_session


# CoinGecko API (무료, API 키 불필요)
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart/range"
COINGECKO_COINS_URL = "https://api.coingecko.com/api/v3/coins/list"


# 코인 심볼 매핑
COIN_ID_MAP = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'DOGE': 'dogecoin',
    'SOL': 'solana',
    'DOT': 'polkadot',
    'MATIC': 'matic-network',
    'LTC': 'litecoin',
}


def get_crypto_data(
    symbol: str,
    start: datetime,
    end: datetime,
    currency: str = 'usd'
) -> pd.DataFrame:
    """
    암호화폐 가격 데이터 조회 (CoinGecko API 사용)

    Args:
        symbol: 암호화폐 심볼 (예: 'BTC', 'ETH')
        start: 시작일
        end: 종료일
        currency: 통화 ('usd', 'krw', 'eur' 등)

    Returns:
        암호화폐 가격 데이터 DataFrame
        Columns: Date, Close, Volume

    Examples:
        >>> get_crypto_data('BTC', datetime(2023, 1, 1), datetime(2023, 12, 31), 'usd')
    """
    # 심볼을 CoinGecko ID로 변환
    coin_id = COIN_ID_MAP.get(symbol.upper(), symbol.lower())

    try:
        # Unix timestamp 변환
        from_timestamp = int(start.timestamp())
        to_timestamp = int(end.timestamp())

        # CoinGecko API 호출
        url = COINGECKO_API_URL.format(coin_id=coin_id)
        params = {
            'vs_currency': currency.lower(),
            'from': from_timestamp,
            'to': to_timestamp
        }

        session = create_session()
        response = get_request(url, params=params, session=session)

        import json
        data = json.loads(response.text)

        if 'prices' not in data:
            print(f"No data found for {symbol}")
            return pd.DataFrame()

        # 가격 데이터 파싱
        prices = data['prices']
        volumes = data.get('total_volumes', [])

        price_data = []
        for i, (timestamp, price) in enumerate(prices):
            date = datetime.fromtimestamp(timestamp / 1000)  # milliseconds to seconds

            volume = volumes[i][1] if i < len(volumes) else 0

            price_data.append({
                'Date': date,
                'Close': price,
                'Volume': volume
            })

        df = pd.DataFrame(price_data)
        df = df.set_index('Date')
        df = df.sort_index()

        return df

    except Exception as e:
        print(f"Warning: CoinGecko API failed for {symbol} ({e})")

        # 대체: Yahoo Finance 사용
        try:
            from ..yahoo import get_yahoo_data

            # 심볼 변환 (BTC -> BTC-USD)
            yahoo_symbol = f"{symbol.upper()}-{currency.upper()}"
            return get_yahoo_data(yahoo_symbol, start, end)

        except Exception as e2:
            print(f"Warning: Yahoo Finance also failed ({e2})")
            return pd.DataFrame()


def parse_crypto_symbol(symbol: str) -> tuple:
    """
    암호화폐 심볼 파싱

    Args:
        symbol: 암호화폐 심볼 (예: 'BTC/USD', 'BTC/KRW', 'BTC')

    Returns:
        (coin_symbol, currency) 튜플

    Examples:
        >>> parse_crypto_symbol('BTC/USD')
        ('BTC', 'USD')
        >>> parse_crypto_symbol('ETH/KRW')
        ('ETH', 'KRW')
        >>> parse_crypto_symbol('BTC')
        ('BTC', 'USD')
    """
    if '/' in symbol:
        parts = symbol.split('/')
        return parts[0].upper(), parts[1].upper()
    else:
        return symbol.upper(), 'USD'
