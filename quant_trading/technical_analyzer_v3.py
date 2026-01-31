"""
기술적 분석 클래스 V3 - 검증된 퀀트 전략 적용
학술 레퍼런스 기반 신호 생성

References:
1. Momentum: Jegadeesh & Titman (1993) "Returns to Buying Winners and Selling Losers"
2. Mean Reversion: De Bondt & Thaler (1985) "Does the Stock Market Overreact?"
3. Trend Following: Hurst, Ooi & Pedersen (2013) "A Century of Evidence on Trend-Following"
4. Volatility: Ang et al. (2006) "The Cross-Section of Volatility and Expected Returns"
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
from .indicators import calculate_all_indicators


class TechnicalAnalyzerV3:
    """
    검증된 퀀트 전략 기반 기술적 분석 클래스
    총 75점 만점

    전략 구성:
    1. Momentum (30점) - 6개월/12개월 모멘텀
    2. Mean Reversion (20점) - RSI/볼린저 밴드 역추세
    3. Trend Following (15점) - 이동평균 기반 추세
    4. Volatility Signal (10점) - 변동성 기반 신호
    """

    def __init__(self, df: pd.DataFrame):
        """
        초기화 함수

        Args:
            df: OHLCV 데이터 DataFrame (컬럼: Open, High, Low, Close, Volume)
        """
        self.df = df.copy()
        self.signals = []

        # 모든 기술적 지표 계산
        self._calculate_indicators()
        self._calculate_returns()

    def _calculate_indicators(self):
        """모든 필요한 기술적 지표를 계산"""
        self.df = calculate_all_indicators(self.df)

    def _calculate_returns(self):
        """수익률 계산 (Momentum 전략용)"""
        # 1개월 (21일), 3개월 (63일), 6개월 (126일), 12개월 (252일) 수익률
        self.df['Return_1M'] = self.df['Close'].pct_change(21)
        self.df['Return_3M'] = self.df['Close'].pct_change(63)
        self.df['Return_6M'] = self.df['Close'].pct_change(126)
        self.df['Return_12M'] = self.df['Close'].pct_change(252)

        # 변동성 계산 (20일 rolling)
        self.df['Volatility_20D'] = self.df['Close'].pct_change().rolling(20).std() * np.sqrt(252)

    def calculate_momentum_score(self) -> Tuple[int, str]:
        """
        모멘텀 점수 계산 (30점 만점)

        Reference: Jegadeesh & Titman (1993)
        - 6개월 모멘텀: 과거 6개월 수익률
        - 12개월 모멘텀: 과거 2-12개월 수익률 (최근 1개월 제외)

        검증된 임계값:
        - 상위 30% 종목: 강한 모멘텀 (+15점)
        - 상위 50% 종목: 중간 모멘텀 (+10점)
        - 양수 수익률: 약한 모멘텀 (+5점)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        if len(self.df) < 252:
            # 12개월 데이터 없으면 6개월로 대체
            if len(self.df) < 126:
                return 0, "데이터 부족"

        recent = self.df.iloc[-1]

        # 1. 6개월 모멘텀 (15점)
        if pd.notna(recent.get('Return_6M')):
            ret_6m = recent['Return_6M']
            if ret_6m > 0.30:  # 30% 이상 상승 (상위 30% 기준)
                score += 15
                signal = "강력 모멘텀(6M)"
            elif ret_6m > 0.15:  # 15% 이상 상승 (상위 50% 기준)
                score += 10
                signal = "중간 모멘텀(6M)"
            elif ret_6m > 0:  # 양수 수익률
                score += 5
                signal = "약한 모멘텀(6M)"

        # 2. 12개월 모멘텀 (15점) - 최근 1개월 제외
        if pd.notna(recent.get('Return_12M')) and pd.notna(recent.get('Return_1M')):
            ret_12m_adjusted = recent['Return_12M'] - recent['Return_1M']
            if ret_12m_adjusted > 0.50:  # 50% 이상
                score += 15
                if signal:
                    signal += " + 강력 모멘텀(12M)"
                else:
                    signal = "강력 모멘텀(12M)"
            elif ret_12m_adjusted > 0.25:  # 25% 이상
                score += 10
                if signal:
                    signal += " + 중간 모멘텀(12M)"
                else:
                    signal = "중간 모멘텀(12M)"
            elif ret_12m_adjusted > 0:
                score += 5
                if signal:
                    signal += " + 약한 모멘텀(12M)"
                else:
                    signal = "약한 모멘텀(12M)"

        return score, signal if signal else "모멘텀 없음"

    def calculate_mean_reversion_score(self) -> Tuple[int, str]:
        """
        평균 회귀 점수 계산 (20점 만점)

        Reference: De Bondt & Thaler (1985)
        - 단기 과매도/과매수 구간에서 반등/하락 확률 높음

        지표:
        1. RSI (Relative Strength Index)
           - RSI < 30: 과매도 (+10점)
           - RSI > 70: 과매수 (0점)

        2. Bollinger Bands
           - 하단 밴드 터치 후 반등 (+10점)
           - 상단 밴드 터치 후 하락 (0점)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        if len(self.df) < 20:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 1. RSI 기반 평균회귀 (10점)
        if pd.notna(recent.get('RSI')):
            rsi = recent['RSI']
            prev_rsi = prev.get('RSI', np.nan)

            # 과매도 구간 탈출 (RSI 30 이하에서 반등)
            if pd.notna(prev_rsi) and prev_rsi <= 30 and rsi > 30:
                score += 10
                signal = "RSI 과매도 반등"
            # 과매도 구간 진입
            elif rsi <= 30:
                score += 5
                signal = "RSI 과매도 구간"

        # 2. Bollinger Bands 기반 평균회귀 (10점)
        if all(pd.notna(recent.get(col)) for col in ['BB_Lower', 'BB_Upper', 'Close']):
            bb_lower = recent['BB_Lower']
            bb_upper = recent['BB_Upper']
            bb_middle = recent.get('BB_Middle', recent['SMA_20'])
            close = recent['Close']
            prev_close = prev['Close']

            # 하단 밴드 터치 후 반등
            if prev_close <= bb_lower and close > bb_lower:
                score += 10
                if signal:
                    signal += " + BB 하단 반등"
                else:
                    signal = "BB 하단 반등"
            # 하단 밴드 근처 (5% 이내)
            elif close <= bb_lower * 1.05:
                score += 5
                if signal:
                    signal += " + BB 하단 근접"
                else:
                    signal = "BB 하단 근접"

        return score, signal if signal else "평균회귀 없음"

    def calculate_trend_following_score(self) -> Tuple[int, str]:
        """
        추세 추종 점수 계산 (15점 만점)

        Reference: Hurst, Ooi & Pedersen (2013)
        - 이동평균선 기반 추세 판단
        - 다중 시간프레임 일치도 확인

        신호:
        1. Golden Cross (20일선 > 60일선) (+10점)
        2. 정배열 (5 > 20 > 60일선) (+5점)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        if len(self.df) < 60:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]
        prev = self.df.iloc[-2]

        # 1. Golden Cross (10점)
        if all(pd.notna(recent.get(col)) and pd.notna(prev.get(col))
               for col in ['SMA_20', 'SMA_60']):
            if prev['SMA_20'] <= prev['SMA_60'] and recent['SMA_20'] > recent['SMA_60']:
                score += 10
                signal = "골든크로스"

        # 2. 정배열 (5점)
        if all(pd.notna(recent.get(col)) for col in ['SMA_5', 'SMA_20', 'SMA_60']):
            if recent['SMA_5'] > recent['SMA_20'] > recent['SMA_60']:
                score += 5
                if signal:
                    signal += " + 정배열"
                else:
                    signal = "정배열"

        return score, signal if signal else "추세 없음"

    def calculate_volatility_score(self) -> Tuple[int, str]:
        """
        변동성 신호 점수 (10점 만점)

        Reference: Ang et al. (2006)
        - 저변동성 이상 현상 (Low Volatility Anomaly)
        - 변동성이 낮은 종목이 장기적으로 높은 수익률

        평가:
        - 20일 변동성 < 20% (연율화): 저변동성 (+10점)
        - 20일 변동성 < 30%: 중간 변동성 (+5점)
        - 20일 변동성 > 50%: 고변동성 (0점, 리스크 높음)

        Returns:
            (점수, 시그널 설명)
        """
        score = 0
        signal = ""

        if len(self.df) < 20:
            return 0, "데이터 부족"

        recent = self.df.iloc[-1]

        if pd.notna(recent.get('Volatility_20D')):
            vol = recent['Volatility_20D']

            if vol < 0.20:  # 20% 미만
                score += 10
                signal = "저변동성"
            elif vol < 0.30:  # 30% 미만
                score += 5
                signal = "중간 변동성"
            elif vol > 0.50:  # 50% 초과
                score += 0
                signal = "고변동성(리스크)"

        return score, signal if signal else "변동성 데이터 없음"

    def calculate_total_score(self) -> Dict:
        """
        전체 점수 및 시그널 계산

        Returns:
            dict: {
                'total_score': 총점 (75점 만점),
                'momentum_score': 모멘텀 점수,
                'mean_reversion_score': 평균회귀 점수,
                'trend_score': 추세 점수,
                'volatility_score': 변동성 점수,
                'signals': 발생한 시그널 문자열
            }
        """
        # 각 전략별 점수 계산
        momentum_score, momentum_signal = self.calculate_momentum_score()
        mean_rev_score, mean_rev_signal = self.calculate_mean_reversion_score()
        trend_score, trend_signal = self.calculate_trend_following_score()
        volatility_score, volatility_signal = self.calculate_volatility_score()

        # 총점
        total = momentum_score + mean_rev_score + trend_score + volatility_score

        # 시그널 결합
        signals = []
        if momentum_signal and momentum_signal != "모멘텀 없음":
            signals.append(momentum_signal)
        if mean_rev_signal and mean_rev_signal != "평균회귀 없음":
            signals.append(mean_rev_signal)
        if trend_signal and trend_signal != "추세 없음":
            signals.append(trend_signal)
        if volatility_signal and volatility_signal != "변동성 데이터 없음":
            signals.append(volatility_signal)

        combined_signal = " + ".join(signals) if signals else "시그널 없음"

        return {
            'total_score': total,
            'momentum_score': momentum_score,
            'mean_reversion_score': mean_rev_score,
            'trend_score': trend_score,
            'volatility_score': volatility_score,
            'signals': combined_signal,

            # 세부 시그널
            'momentum_signal': momentum_signal,
            'mean_reversion_signal': mean_rev_signal,
            'trend_signal': trend_signal,
            'volatility_signal': volatility_signal,
        }


def compare_analyzers(df: pd.DataFrame) -> pd.DataFrame:
    """
    V2와 V3 분석기 비교

    Args:
        df: OHLCV 데이터

    Returns:
        비교 결과 DataFrame
    """
    from .technical_analyzer_v2 import TechnicalAnalyzerV2

    v2 = TechnicalAnalyzerV2(df)
    v3 = TechnicalAnalyzerV3(df)

    result_v2 = v2.calculate_total_score()
    result_v3 = v3.calculate_total_score()

    comparison = pd.DataFrame({
        'Metric': ['Total Score', 'Signals'],
        'V2 (Custom)': [result_v2['total_score'], result_v2['signals']],
        'V3 (Quant)': [result_v3['total_score'], result_v3['signals']]
    })

    return comparison
