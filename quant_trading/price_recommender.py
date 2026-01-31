"""
가격 추천 시스템 (Price Recommender)
기술적 분석 기반 매수/매도/손절 가격 제시

References:
1. Support/Resistance: Murphy's Technical Analysis (1999)
2. ATR-based Stop Loss: Wilder's "New Concepts in Technical Trading Systems" (1978)
3. Risk/Reward Ratio: Standard 2:1 or 3:1 ratio
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class PriceRecommender:
    """
    기술적 분석 기반 가격 추천 클래스
    매수가, 매도가, 손절가 계산
    """

    def __init__(self, df: pd.DataFrame, current_price: float):
        """
        초기화

        Args:
            df: OHLCV 데이터
            current_price: 현재가
        """
        self.df = df.copy()
        self.current_price = current_price
        self._calculate_indicators()

    def _calculate_indicators(self):
        """필요한 기술적 지표 계산"""
        # 이동평균선
        self.df['SMA_20'] = self.df['Close'].rolling(window=20).mean()
        self.df['SMA_60'] = self.df['Close'].rolling(window=60).mean()

        # 볼린저 밴드
        self.df['BB_Middle'] = self.df['Close'].rolling(window=20).mean()
        bb_std = self.df['Close'].rolling(window=20).std()
        self.df['BB_Upper'] = self.df['BB_Middle'] + (bb_std * 2)
        self.df['BB_Lower'] = self.df['BB_Middle'] - (bb_std * 2)

        # ATR (Average True Range) - 변동성 측정
        high_low = self.df['High'] - self.df['Low']
        high_close = np.abs(self.df['High'] - self.df['Close'].shift())
        low_close = np.abs(self.df['Low'] - self.df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        self.df['ATR'] = true_range.rolling(window=14).mean()

    def calculate_support_resistance(self, lookback: int = 60) -> Tuple[float, float]:
        """
        지지선/저항선 계산

        Args:
            lookback: 과거 몇일치 데이터를 볼 것인가

        Returns:
            (지지선, 저항선)
        """
        recent_data = self.df.tail(lookback)

        # 최근 저점들의 평균 = 지지선
        lows = recent_data['Low'].nsmallest(5)
        support = lows.mean()

        # 최근 고점들의 평균 = 저항선
        highs = recent_data['High'].nlargest(5)
        resistance = highs.mean()

        return support, resistance

    def calculate_fibonacci_levels(self) -> Dict[str, float]:
        """
        피보나치 되돌림 레벨 계산 (최근 60일 기준)

        Returns:
            dict: 피보나치 레벨
        """
        recent_data = self.df.tail(60)
        high = recent_data['High'].max()
        low = recent_data['Low'].min()
        diff = high - low

        # 피보나치 비율
        fib_levels = {
            'High': high,
            'Fib_0.236': high - (diff * 0.236),
            'Fib_0.382': high - (diff * 0.382),
            'Fib_0.500': high - (diff * 0.500),
            'Fib_0.618': high - (diff * 0.618),
            'Fib_0.786': high - (diff * 0.786),
            'Low': low,
        }

        return fib_levels

    def calculate_entry_price(self) -> Dict[str, float]:
        """
        매수 진입가 계산

        Returns:
            dict: {
                'aggressive': 공격적 매수가 (현재가),
                'moderate': 중도적 매수가 (소폭 하락 대기),
                'conservative': 보수적 매수가 (지지선 근처)
            }
        """
        support, _ = self.calculate_support_resistance()
        recent = self.df.iloc[-1]

        # 1. 공격적: 현재가 매수
        aggressive = self.current_price

        # 2. 중도적: 현재가에서 2-3% 하락 지점 (20일 이평선 근처)
        if pd.notna(recent.get('SMA_20')):
            moderate = min(self.current_price * 0.97, recent['SMA_20'])
        else:
            moderate = self.current_price * 0.97

        # 3. 보수적: 지지선 근처 (5% 이내)
        conservative = support * 1.02

        return {
            'aggressive': round(aggressive, 2),
            'moderate': round(moderate, 2),
            'conservative': round(conservative, 2)
        }

    def calculate_exit_price(self, entry_price: float, risk_reward_ratio: float = 2.0) -> Dict[str, float]:
        """
        매도 청산가 계산

        Args:
            entry_price: 진입가격
            risk_reward_ratio: 손익비 (기본 2:1)

        Returns:
            dict: {
                'target_1': 1차 목표가 (저항선),
                'target_2': 2차 목표가 (리스크/리워드 기준),
                'target_3': 3차 목표가 (볼린저 상단)
            }
        """
        _, resistance = self.calculate_support_resistance()
        recent = self.df.iloc[-1]
        atr = recent.get('ATR', self.current_price * 0.02)

        # 1차 목표: 저항선
        target_1 = resistance

        # 2차 목표: ATR 기반 리스크/리워드 (2:1 또는 3:1)
        # 손실 = 1 ATR, 이익 = 2 ATR or 3 ATR
        target_2 = entry_price + (atr * risk_reward_ratio)

        # 3차 목표: 볼린저 밴드 상단
        if pd.notna(recent.get('BB_Upper')):
            target_3 = recent['BB_Upper']
        else:
            target_3 = entry_price * 1.10  # 10% 상승

        return {
            'target_1': round(target_1, 2),
            'target_2': round(target_2, 2),
            'target_3': round(target_3, 2)
        }

    def calculate_stop_loss(self, entry_price: float) -> Dict[str, float]:
        """
        손절가 계산 (ATR 기반)

        Args:
            entry_price: 진입가격

        Returns:
            dict: {
                'tight': 타이트한 손절 (1 ATR),
                'normal': 일반 손절 (1.5 ATR),
                'wide': 여유있는 손절 (2 ATR)
            }
        """
        recent = self.df.iloc[-1]
        atr = recent.get('ATR', self.current_price * 0.02)

        # ATR 배수에 따른 손절선
        tight = entry_price - (atr * 1.0)
        normal = entry_price - (atr * 1.5)
        wide = entry_price - (atr * 2.0)

        return {
            'tight': round(tight, 2),
            'normal': round(normal, 2),
            'wide': round(wide, 2)
        }

    def get_recommendation(self, strategy: str = 'moderate') -> Dict:
        """
        전체 가격 추천 (매수/매도/손절)

        Args:
            strategy: 'aggressive', 'moderate', 'conservative'

        Returns:
            dict: 전체 추천 가격
        """
        # 매수가
        entry_prices = self.calculate_entry_price()
        entry_price = entry_prices[strategy]

        # 매도가
        exit_prices = self.calculate_exit_price(entry_price)

        # 손절가
        stop_losses = self.calculate_stop_loss(entry_price)

        # 지지/저항
        support, resistance = self.calculate_support_resistance()

        # 피보나치
        fib_levels = self.calculate_fibonacci_levels()

        # 기대 수익률 계산
        expected_profit_1 = ((exit_prices['target_1'] - entry_price) / entry_price) * 100
        expected_profit_2 = ((exit_prices['target_2'] - entry_price) / entry_price) * 100
        expected_profit_3 = ((exit_prices['target_3'] - entry_price) / entry_price) * 100

        # 손실 위험 계산
        expected_loss = ((entry_price - stop_losses['normal']) / entry_price) * 100

        # 리스크/리워드 비율
        risk_reward_ratio = expected_profit_2 / expected_loss if expected_loss > 0 else 0

        return {
            'current_price': self.current_price,
            'strategy': strategy,

            # 매수가
            'entry': {
                'price': entry_price,
                'all_options': entry_prices,
            },

            # 매도가 (목표가)
            'exit': {
                'target_1': exit_prices['target_1'],
                'target_2': exit_prices['target_2'],
                'target_3': exit_prices['target_3'],
                'expected_profit_1': round(expected_profit_1, 2),
                'expected_profit_2': round(expected_profit_2, 2),
                'expected_profit_3': round(expected_profit_3, 2),
            },

            # 손절가
            'stop_loss': {
                'price': stop_losses['normal'],
                'all_options': stop_losses,
                'expected_loss': round(expected_loss, 2),
            },

            # 리스크/리워드
            'risk_reward_ratio': round(risk_reward_ratio, 2),

            # 기술적 레벨
            'technical_levels': {
                'support': round(support, 2),
                'resistance': round(resistance, 2),
                'fib_0.382': round(fib_levels['Fib_0.382'], 2),
                'fib_0.500': round(fib_levels['Fib_0.500'], 2),
                'fib_0.618': round(fib_levels['Fib_0.618'], 2),
            }
        }


def print_price_recommendation(recommendation: Dict, ticker: str = ""):
    """
    가격 추천 결과를 보기 좋게 출력

    Args:
        recommendation: 추천 결과
        ticker: 종목 티커
    """
    r = recommendation

    print(f"\n{'='*70}")
    print(f"가격 추천 {f'- {ticker}' if ticker else ''} (전략: {r['strategy'].upper()})")
    print(f"{'='*70}\n")

    print(f"현재가: ${r['current_price']:.2f}")
    print(f"\n[매수 가격]")
    print(f"  추천 매수가: ${r['entry']['price']:.2f}")
    print(f"  (공격적: ${r['entry']['all_options']['aggressive']:.2f} | "
          f"중도: ${r['entry']['all_options']['moderate']:.2f} | "
          f"보수: ${r['entry']['all_options']['conservative']:.2f})")

    print(f"\n[매도 목표가]")
    print(f"  1차 목표: ${r['exit']['target_1']:.2f} (+{r['exit']['expected_profit_1']:.1f}%) - 저항선")
    print(f"  2차 목표: ${r['exit']['target_2']:.2f} (+{r['exit']['expected_profit_2']:.1f}%) - R/R 기준")
    print(f"  3차 목표: ${r['exit']['target_3']:.2f} (+{r['exit']['expected_profit_3']:.1f}%) - 볼린저 상단")

    print(f"\n[손절 가격]")
    print(f"  추천 손절가: ${r['stop_loss']['price']:.2f} ({r['stop_loss']['expected_loss']:.1f}%)")
    print(f"  (타이트: ${r['stop_loss']['all_options']['tight']:.2f} | "
          f"일반: ${r['stop_loss']['all_options']['normal']:.2f} | "
          f"여유: ${r['stop_loss']['all_options']['wide']:.2f})")

    print(f"\n[리스크/리워드 비율]")
    print(f"  R/R: {r['risk_reward_ratio']:.2f}:1", end="")
    if r['risk_reward_ratio'] >= 2.0:
        print(" (양호)")
    elif r['risk_reward_ratio'] >= 1.5:
        print(" (보통)")
    else:
        print(" (낮음 - 주의)")

    print(f"\n[기술적 레벨]")
    print(f"  지지선: ${r['technical_levels']['support']:.2f}")
    print(f"  저항선: ${r['technical_levels']['resistance']:.2f}")
    print(f"  Fib 38.2%: ${r['technical_levels']['fib_0.382']:.2f}")
    print(f"  Fib 50.0%: ${r['technical_levels']['fib_0.500']:.2f}")
    print(f"  Fib 61.8%: ${r['technical_levels']['fib_0.618']:.2f}")

    print(f"\n{'='*70}")
    print("추천 전략:")
    print(f"{'='*70}")
    if r['strategy'] == 'aggressive':
        print("  - 즉시 매수 (현재가)")
        print("  - 분할 매도: 1차 목표 50%, 2차 목표 30%, 3차 목표 20%")
    elif r['strategy'] == 'moderate':
        print("  - 소폭 하락 시 매수 (2-3% 하락 대기)")
        print("  - 분할 매도: 1차 목표 40%, 2차 목표 40%, 3차 목표 20%")
    else:  # conservative
        print("  - 지지선 근처까지 대기 후 매수")
        print("  - 분할 매도: 1차 목표 30%, 2차 목표 50%, 3차 목표 20%")

    print(f"  - 손절: ${r['stop_loss']['price']:.2f} 이탈 시 즉시 청산")
    print()
