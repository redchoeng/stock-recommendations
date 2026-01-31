"""
기술적 분석 클래스 V2 (개선 버전)
직접 구현한 지표로 전체 기능 활용
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from .indicators import calculate_all_indicators


class TechnicalAnalyzerV2:
    """
    기술적 분석을 수행하고 점수를 계산하는 클래스 (개선 버전)
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

        # 모든 기술적 지표 계산
        self._calculate_indicators()

    def _calculate_indicators(self):
        """모든 필요한 기술적 지표를 계산"""
        self.df = calculate_all_indicators(self.df)

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

        # 필수 컬럼 확인
        required_cols = ['Ichimoku_Conversion', 'Ichimoku_Base', 'Ichimoku_SpanA', 'Ichimoku_SpanB']
        if not all(col in self.df.columns for col in required_cols):
            return 0, "일목 데이터 없음"

        if len(self.df) < 52:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 선행스팬B (구름대 상단) - 더 높은 값이 상단
        cloud_top = max(recent['Ichimoku_SpanA'], recent['Ichimoku_SpanB'])
        cloud_bottom = min(recent['Ichimoku_SpanA'], recent['Ichimoku_SpanB'])

        # 주가가 구름대 아래면 탈락
        if pd.notna(cloud_top) and recent['Close'] < cloud_top:
            return 0, "역배열(구름대 아래)"

        # 강력 돌파: 주가가 구름대를 강한 거래량으로 돌파 (+10점)
        if pd.notna(cloud_top) and pd.notna(prev.get('Ichimoku_SpanB')):
            prev_cloud_top = max(prev['Ichimoku_SpanA'], prev['Ichimoku_SpanB'])
            volume_ratio = recent['Volume'] / prev['Volume'] if prev['Volume'] > 0 else 0

            if (prev['Close'] <= prev_cloud_top and
                recent['Close'] > cloud_top and
                volume_ratio >= 1.5):
                score += 10
                signal = "일목 강력돌파"

        # 눌림목: 구름대 위에서 전환선/기준선 지지 (+10점)
        if pd.notna(cloud_top) and recent['Close'] > cloud_top:
            for i in range(1, min(4, len(self.df))):
                day = self.df.iloc[-i]

                # 전환선 또는 기준선 터치 확인
                if pd.notna(day.get('Ichimoku_Conversion')) and pd.notna(day.get('Ichimoku_Base')):
                    touched_conversion = (day['Low'] <= day['Ichimoku_Conversion'] <= day['High'])
                    touched_base = (day['Low'] <= day['Ichimoku_Base'] <= day['High'])

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

        if len(self.df) < 20:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 볼린저 밴드 사용
        if 'BB_Lower' in self.df.columns and 'BB_Upper' in self.df.columns:
            bb_lower = recent['BB_Lower']
            bb_upper = recent['BB_Upper']

            # 볼린저 상단이 우상향 중인지 확인 (최근 5일)
            if pd.notna(bb_upper):
                upper_trend = self.df['BB_Upper'].iloc[-5:].is_monotonic_increasing

                # 하단 밴드 터치 후 반등 양봉
                if pd.notna(bb_lower):
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

        if len(self.df) < 20:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 필수 컬럼 확인
        short_k = 'STOCH_K_5_3_3'
        short_d = 'STOCH_D_5_3_3'
        mid_k = 'STOCH_K_10_6_6'
        long_k = 'STOCH_K_20_12_12'

        if not all(col in self.df.columns for col in [short_k, short_d, mid_k, long_k]):
            return 0, "스토캐스틱 데이터 없음"

        # 바닥 잡기: 중기&장기 침체권(20 이하) + 단기 골든크로스 (+15점)
        mid_oversold = pd.notna(recent.get(mid_k)) and recent[mid_k] <= 20
        long_oversold = pd.notna(recent.get(long_k)) and recent[long_k] <= 20

        # 단기 골든크로스: %K가 %D를 상향 돌파
        if (pd.notna(prev.get(short_k)) and pd.notna(prev.get(short_d)) and
            pd.notna(recent.get(short_k)) and pd.notna(recent.get(short_d))):

            short_golden = (prev[short_k] <= prev[short_d] and
                           recent[short_k] > recent[short_d])

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
                if not np.isnan(rsi_values[i]):
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
        if pd.notna(prev.get('RSI')) and pd.notna(recent.get('RSI')):
            if prev['RSI'] <= 30 and recent['RSI'] > 30:
                score += 10
                signal = "RSI 과매도 탈출"

        return score, signal

    def calculate_total_score(self) -> Dict:
        """
        전체 기술적 분석 점수 계산 (75점 만점)

        Returns:
            dict: 점수 및 시그널 정보
        """
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
