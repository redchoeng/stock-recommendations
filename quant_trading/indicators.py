"""
기술적 지표 직접 구현 (pandas-ta 대체)
Python 3.14에서도 작동하도록 순수 pandas/numpy로 구현
"""

import pandas as pd
import numpy as np


def calculate_sma(df, periods=[5, 20, 60, 120]):
    """
    단순 이동평균선 (Simple Moving Average)

    Args:
        df: OHLCV DataFrame
        periods: 기간 리스트

    Returns:
        DataFrame with SMA columns added
    """
    for period in periods:
        df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
    return df


def calculate_ema(df, periods=[12, 26]):
    """
    지수 이동평균선 (Exponential Moving Average)

    Args:
        df: OHLCV DataFrame
        periods: 기간 리스트

    Returns:
        DataFrame with EMA columns added
    """
    for period in periods:
        df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
    return df


def calculate_rsi(df, period=14):
    """
    RSI (Relative Strength Index) 계산

    Args:
        df: OHLCV DataFrame
        period: RSI 기간 (기본 14)

    Returns:
        DataFrame with RSI column added
    """
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df


def calculate_macd(df, fast=12, slow=26, signal=9):
    """
    MACD (Moving Average Convergence Divergence)

    Args:
        df: OHLCV DataFrame
        fast: 빠른 EMA 기간
        slow: 느린 EMA 기간
        signal: 시그널선 기간

    Returns:
        DataFrame with MACD columns added
    """
    df['EMA_fast'] = df['Close'].ewm(span=fast, adjust=False).mean()
    df['EMA_slow'] = df['Close'].ewm(span=slow, adjust=False).mean()

    df['MACD'] = df['EMA_fast'] - df['EMA_slow']
    df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    return df


def calculate_bollinger_bands(df, period=20, std=2):
    """
    볼린저 밴드 (Bollinger Bands)

    Args:
        df: OHLCV DataFrame
        period: 기간
        std: 표준편차 배수

    Returns:
        DataFrame with BB columns added
    """
    df['BB_Middle'] = df['Close'].rolling(window=period).mean()
    df['BB_Std'] = df['Close'].rolling(window=period).std()

    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * std)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * std)

    return df


def calculate_stochastic(df, k_period=14, d_period=3, smooth_k=3):
    """
    스토캐스틱 오실레이터 (Stochastic Oscillator)

    Args:
        df: OHLCV DataFrame
        k_period: %K 기간
        d_period: %D 기간 (신호선)
        smooth_k: %K 스무딩 기간

    Returns:
        DataFrame with Stochastic columns added
    """
    # 최고가/최저가
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()

    # %K 계산
    stoch_k = 100 * (df['Close'] - low_min) / (high_max - low_min)

    # %K 스무딩
    df[f'STOCH_K_{k_period}_{d_period}_{smooth_k}'] = stoch_k.rolling(window=smooth_k).mean()

    # %D 계산 (시그널선)
    df[f'STOCH_D_{k_period}_{d_period}_{smooth_k}'] = df[f'STOCH_K_{k_period}_{d_period}_{smooth_k}'].rolling(window=d_period).mean()

    return df


def calculate_ichimoku(df):
    """
    일목균형표 (Ichimoku Cloud)

    Returns:
        DataFrame with Ichimoku columns added
    """
    # 전환선 (Conversion Line): (9일 최고가 + 9일 최저가) / 2
    high_9 = df['High'].rolling(window=9).max()
    low_9 = df['Low'].rolling(window=9).min()
    df['Ichimoku_Conversion'] = (high_9 + low_9) / 2

    # 기준선 (Base Line): (26일 최고가 + 26일 최저가) / 2
    high_26 = df['High'].rolling(window=26).max()
    low_26 = df['Low'].rolling(window=26).min()
    df['Ichimoku_Base'] = (high_26 + low_26) / 2

    # 선행스팬 A (Leading Span A): (전환선 + 기준선) / 2
    df['Ichimoku_SpanA'] = ((df['Ichimoku_Conversion'] + df['Ichimoku_Base']) / 2).shift(26)

    # 선행스팬 B (Leading Span B): (52일 최고가 + 52일 최저가) / 2
    high_52 = df['High'].rolling(window=52).max()
    low_52 = df['Low'].rolling(window=52).min()
    df['Ichimoku_SpanB'] = ((high_52 + low_52) / 2).shift(26)

    # 후행스팬 (Lagging Span): 현재 종가를 26일 뒤로
    df['Ichimoku_Lagging'] = df['Close'].shift(-26)

    return df


def calculate_atr(df, period=14):
    """
    ATR (Average True Range) - 변동성 지표

    Args:
        df: OHLCV DataFrame
        period: ATR 기간

    Returns:
        DataFrame with ATR column added
    """
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)

    df['ATR'] = true_range.rolling(window=period).mean()

    return df


def calculate_obv(df):
    """
    OBV (On Balance Volume) - 거래량 지표

    Returns:
        DataFrame with OBV column added
    """
    obv = [0]

    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['Close'].iloc[i-1]:
            obv.append(obv[-1] + df['Volume'].iloc[i])
        elif df['Close'].iloc[i] < df['Close'].iloc[i-1]:
            obv.append(obv[-1] - df['Volume'].iloc[i])
        else:
            obv.append(obv[-1])

    df['OBV'] = obv

    return df


def calculate_all_indicators(df):
    """
    모든 기술적 지표 한번에 계산

    Args:
        df: OHLCV DataFrame

    Returns:
        모든 지표가 추가된 DataFrame
    """
    df = df.copy()

    # 이동평균
    df = calculate_sma(df, periods=[5, 20, 60, 120])
    df = calculate_ema(df, periods=[12, 26])

    # 모멘텀 지표
    df = calculate_rsi(df, period=14)
    df = calculate_macd(df)

    # 변동성 지표
    df = calculate_bollinger_bands(df, period=20, std=2)
    df = calculate_atr(df, period=14)

    # 스토캐스틱 (단기, 중기, 장기)
    df = calculate_stochastic(df, k_period=5, d_period=3, smooth_k=3)  # 단기
    df = calculate_stochastic(df, k_period=10, d_period=6, smooth_k=6)  # 중기
    df = calculate_stochastic(df, k_period=20, d_period=12, smooth_k=12)  # 장기

    # 일목균형표
    df = calculate_ichimoku(df)

    # 거래량 지표
    df = calculate_obv(df)

    return df


def get_indicator_names():
    """계산 가능한 모든 지표 이름 반환"""
    return {
        'trend': ['SMA_5', 'SMA_20', 'SMA_60', 'SMA_120', 'EMA_12', 'EMA_26'],
        'momentum': ['RSI', 'MACD', 'MACD_Signal', 'MACD_Hist'],
        'volatility': ['BB_Upper', 'BB_Middle', 'BB_Lower', 'ATR'],
        'stochastic': [
            'STOCH_K_5_3_3', 'STOCH_D_5_3_3',
            'STOCH_K_10_6_6', 'STOCH_D_10_6_6',
            'STOCH_K_20_12_12', 'STOCH_D_20_12_12'
        ],
        'ichimoku': [
            'Ichimoku_Conversion', 'Ichimoku_Base',
            'Ichimoku_SpanA', 'Ichimoku_SpanB', 'Ichimoku_Lagging'
        ],
        'volume': ['OBV']
    }
