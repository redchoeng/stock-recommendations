"""
기술적 분석 클래스 (Technical Analyzer)
pandas-ta 라이브러리를 활용한 기술적 지표 분석 및 점수 계산
"""

import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, Tuple


class TechnicalAnalyzer:
    """
    기술적 분석을 수행하고 점수를 계산하는 클래스
    총 75점 만점
    """

    def __init__(self, df: pd.DataFrame):
        """
        초기화 함수

        Args:
            df: OHLCV 데이터 DataFrame (컬럼: Open, High, Low, Close, Volume)
        """
        self.df = df.copy()
        self.signals = []  # 발생한 시그널 목록

        # 필수 지표 계산
        self._calculate_indicators()

    def _calculate_indicators(self):
        """모든 필요한 기술적 지표를 계산"""

        # 1. 이동평균선 (SMA)
        self.df['SMA_5'] = ta.sma(self.df['Close'], length=5)
        self.df['SMA_20'] = ta.sma(self.df['Close'], length=20)
        self.df['SMA_60'] = ta.sma(self.df['Close'], length=60)
        self.df['SMA_120'] = ta.sma(self.df['Close'], length=120)

        # 2. 일목균형표 (Ichimoku Cloud)
        ichimoku = ta.ichimoku(self.df['High'], self.df['Low'], self.df['Close'])
        if ichimoku is not None and len(ichimoku) > 0:
            self.df = pd.concat([self.df, ichimoku[0]], axis=1)

        # 3. 볼린저 밴드 (Bollinger Bands)
        bbands = ta.bbands(self.df['Close'], length=20, std=2)
        if bbands is not None:
            self.df = pd.concat([self.df, bbands], axis=1)

        # 4. 켈트너 채널 (Keltner Channel)
        kc = ta.kc(self.df['High'], self.df['Low'], self.df['Close'], length=20)
        if kc is not None:
            self.df = pd.concat([self.df, kc], axis=1)

        # 5. 스토캐스틱 (Stochastic) - 단기, 중기, 장기
        # 단기 (5,3,3)
        stoch_short = ta.stoch(self.df['High'], self.df['Low'], self.df['Close'],
                               k=5, d=3, smooth_k=3)
        if stoch_short is not None:
            self.df['STOCH_SHORT_K'] = stoch_short['STOCHk_5_3_3']
            self.df['STOCH_SHORT_D'] = stoch_short['STOCHd_5_3_3']

        # 중기 (10,6,6)
        stoch_mid = ta.stoch(self.df['High'], self.df['Low'], self.df['Close'],
                             k=10, d=6, smooth_k=6)
        if stoch_mid is not None:
            self.df['STOCH_MID_K'] = stoch_mid['STOCHk_10_6_6']
            self.df['STOCH_MID_D'] = stoch_mid['STOCHd_10_6_6']

        # 장기 (20,12,12)
        stoch_long = ta.stoch(self.df['High'], self.df['Low'], self.df['Close'],
                              k=20, d=12, smooth_k=12)
        if stoch_long is not None:
            self.df['STOCH_LONG_K'] = stoch_long['STOCHk_20_12_12']
            self.df['STOCH_LONG_D'] = stoch_long['STOCHd_20_12_12']

        # 6. RSI (Relative Strength Index)
        self.df['RSI'] = ta.rsi(self.df['Close'], length=14)

    def calculate_moving_average_score(self) -> Tuple[int, str]:
        """
        이동평균선 점수 계산 (15점 만점)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        if len(self.df) < 120:
            return 0, "데이터 부족"

        # 최근 데이터
        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 골든크로스: 20일선이 60일선을 상향 돌파 (+10점)
        if (prev['SMA_20'] <= prev['SMA_60'] and
            recent['SMA_20'] > recent['SMA_60']):
            score += 10
            signal = "골든크로스"

        # 정배열: 5일 > 20일 > 60일 > 120일 (+5점)
        if (recent['SMA_5'] > recent['SMA_20'] >
            recent['SMA_60'] > recent['SMA_120']):
            score += 5
            if signal:
                signal += " + 정배열"
            else:
                signal = "정배열"

        return score, signal

    def calculate_ichimoku_score(self) -> Tuple[int, str]:
        """
        일목균형표 점수 계산 (20점 만점)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        # 일목균형표 컬럼 확인
        required_cols = ['ISA_9', 'ISB_26', 'ITS_9', 'IKS_26', 'ICS_26']
        if not all(col in self.df.columns for col in required_cols):
            return 0, "일목 데이터 없음"

        if len(self.df) < 30:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 선행스팬2 (구름대 상단) - ISB_26 (Leading Span B)
        senkou_span_b = recent['ISB_26']

        # 주가가 구름대 아래면 탈락
        if recent['Close'] < senkou_span_b:
            return 0, "역배열(구름대 아래)"

        # 강력 돌파: 주가가 선행스팬2를 강한 거래량으로 돌파 (+10점)
        volume_ratio = recent['Volume'] / prev['Volume'] if prev['Volume'] > 0 else 0

        if (prev['Close'] <= prev['ISB_26'] and
            recent['Close'] > senkou_span_b and
            volume_ratio >= 1.5):
            score += 10
            signal = "일목 강력돌파"

        # 눌림목: 구름대 위에서 전환선/기준선 지지 (+10점)
        # 최근 3일 이내 전환선(ITS_9) 또는 기준선(IKS_26) 터치 후 양봉
        if recent['Close'] > senkou_span_b:
            for i in range(1, min(4, len(self.df))):
                day = self.df.iloc[-i]

                # 전환선 또는 기준선 지지 확인
                touched_conversion = (day['Low'] <= day['ITS_9'] <= day['High'])
                touched_base = (day['Low'] <= day['IKS_26'] <= day['High'])

                # 최근일 양봉 확인
                is_green = recent['Close'] > recent['Open']

                if (touched_conversion or touched_base) and is_green:
                    score += 10
                    if signal:
                        signal += " + 눌림목"
                    else:
                        signal = "일목 눌림목"
                    break

        return score, signal

    def calculate_channel_score(self) -> Tuple[int, str]:
        """
        채널 및 변동성 점수 계산 (10점 만점)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        if len(self.df) < 5:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 켈트너 채널 사용 (BBL_20_2.0 = 볼린저 하단, KCL = 켈트너 하단)
        if 'BBL_20_2.0' in self.df.columns and 'BBU_20_2.0' in self.df.columns:
            bb_lower = recent['BBL_20_2.0']
            bb_upper = recent['BBU_20_2.0']

            # 볼린저 상단이 우상향 중인지 확인 (최근 5일)
            upper_trend = self.df['BBU_20_2.0'].iloc[-5:].is_monotonic_increasing

            # 하단 밴드 터치 후 반등 양봉
            touched_lower = (prev['Low'] <= bb_lower and prev['Close'] > bb_lower)
            is_green = recent['Close'] > recent['Open']

            if upper_trend and touched_lower and is_green:
                score += 10
                signal = "채널 하단 반등"

        return score, signal

    def calculate_stochastic_score(self) -> Tuple[int, str]:
        """
        스토캐스틱 점수 계산 - 멀티 타임프레임 (15점 만점)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        if len(self.df) < 2:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 필수 컬럼 확인
        required = ['STOCH_SHORT_K', 'STOCH_SHORT_D',
                   'STOCH_MID_K', 'STOCH_LONG_K']

        if not all(col in self.df.columns for col in required):
            return 0, "스토캐스틱 데이터 없음"

        # 바닥 잡기: 중기&장기 침체권(20 이하) + 단기 골든크로스 (+15점)
        mid_oversold = recent['STOCH_MID_K'] <= 20
        long_oversold = recent['STOCH_LONG_K'] <= 20

        # 단기 골든크로스: %K가 %D를 상향 돌파
        short_golden = (prev['STOCH_SHORT_K'] <= prev['STOCH_SHORT_D'] and
                       recent['STOCH_SHORT_K'] > recent['STOCH_SHORT_D'])

        if mid_oversold and long_oversold and short_golden:
            score += 15
            signal = "스토캐스틱 바닥 골든크로스"

        return score, signal

    def calculate_rsi_score(self) -> Tuple[int, str]:
        """
        RSI 점수 계산 - 다이버전스 (15점 만점)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        if len(self.df) < 20:
            return 0, "데이터 부족"

        if 'RSI' not in self.df.columns:
            return 0, "RSI 데이터 없음"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 최근 20일 데이터
        last_20 = self.df.iloc[-20:]

        # 상승 다이버전스: 주가 신저가 + RSI 저점 상승 (+15점)
        # 최근 저점 2개 찾기
        low_prices = last_20['Low'].values
        rsi_values = last_20['RSI'].values

        # 저점 찾기 (local minima)
        price_lows = []
        rsi_lows = []

        for i in range(1, len(low_prices) - 1):
            if low_prices[i] < low_prices[i-1] and low_prices[i] < low_prices[i+1]:
                price_lows.append((i, low_prices[i]))
                rsi_lows.append((i, rsi_values[i]))

        # 다이버전스 확인: 최소 2개의 저점 필요
        if len(price_lows) >= 2:
            # 최근 2개 저점
            recent_price_low = price_lows[-1][1]
            prev_price_low = price_lows[-2][1]

            recent_rsi_low = rsi_lows[-1][1]
            prev_rsi_low = rsi_lows[-2][1]

            # 다이버전스: 주가는 하락, RSI는 상승
            if recent_price_low < prev_price_low and recent_rsi_low > prev_rsi_low:
                score += 15
                signal = "RSI 상승 다이버전스"
                return score, signal

        # 과매도 탈출: RSI 30 이하 → 30 초과 (+10점)
        if prev['RSI'] <= 30 and recent['RSI'] > 30:
            score += 10
            signal = "RSI 과매도 탈출"

        return score, signal

    def calculate_total_score(self) -> Dict:
        """
        전체 기술적 분석 점수 계산 (75점 만점)

        Returns:
            dict: {
                'total_score': 총점,
                'ma_score': 이동평균 점수,
                'ichimoku_score': 일목 점수,
                'channel_score': 채널 점수,
                'stoch_score': 스토캐스틱 점수,
                'rsi_score': RSI 점수,
                'signals': 시그널 목록
            }
        """
        results = {}

        # 각 지표별 점수 계산
        ma_score, ma_signal = self.calculate_moving_average_score()
        ichimoku_score, ichimoku_signal = self.calculate_ichimoku_score()
        channel_score, channel_signal = self.calculate_channel_score()
        stoch_score, stoch_signal = self.calculate_stochastic_score()
        rsi_score, rsi_signal = self.calculate_rsi_score()

        # 총점 계산
        total = ma_score + ichimoku_score + channel_score + stoch_score + rsi_score

        # 시그널 수집
        signals = []
        if ma_signal:
            signals.append(ma_signal)
        if ichimoku_signal:
            signals.append(ichimoku_signal)
        if channel_signal:
            signals.append(channel_signal)
        if stoch_signal:
            signals.append(stoch_signal)
        if rsi_signal:
            signals.append(rsi_signal)

        results = {
            'total_score': total,
            'ma_score': ma_score,
            'ichimoku_score': ichimoku_score,
            'channel_score': channel_score,
            'stoch_score': stoch_score,
            'rsi_score': rsi_score,
            'signals': ' + '.join(signals) if signals else '시그널 없음'
        }

        return results
