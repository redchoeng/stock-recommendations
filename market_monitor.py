"""
시장 급변 감지 모듈
S&P500 지수, VIX, 뉴스 감성 변화 모니터링
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '.')

from quant_trading.news_sentiment_analyzer import NewsSentimentAnalyzer


class MarketMonitor:
    """시장 급변 감지 클래스"""

    def __init__(self):
        self.spy = yf.Ticker('SPY')
        self.vix = yf.Ticker('^VIX')

        # 임계값 설정
        self.CRASH_THRESHOLD = -3.0  # -3% 이상 하락
        self.SURGE_THRESHOLD = 3.0   # +3% 이상 상승
        self.VIX_THRESHOLD = 25.0    # VIX 25 이상
        self.NEWS_CHANGE_THRESHOLD = 30.0  # 뉴스 점수 30% 이상 변화

    def check_spy_change(self):
        """
        S&P500 지수 변화 체크

        Returns:
            dict: {
                'change_pct': float,
                'alert': bool,
                'alert_type': 'crash' or 'surge' or None
            }
        """
        try:
            # 최근 2일 데이터
            df = self.spy.history(period='2d')

            if len(df) < 2:
                return {'change_pct': 0, 'alert': False, 'alert_type': None}

            # 전일 대비 변화율
            prev_close = df['Close'].iloc[-2]
            curr_close = df['Close'].iloc[-1]
            change_pct = ((curr_close - prev_close) / prev_close) * 100

            # 급변 감지
            alert = False
            alert_type = None

            if change_pct <= self.CRASH_THRESHOLD:
                alert = True
                alert_type = 'crash'
            elif change_pct >= self.SURGE_THRESHOLD:
                alert = True
                alert_type = 'surge'

            return {
                'change_pct': change_pct,
                'current': curr_close,
                'previous': prev_close,
                'alert': alert,
                'alert_type': alert_type
            }

        except Exception as e:
            print(f"[ERROR] SPY 체크 실패: {e}")
            return {'change_pct': 0, 'alert': False, 'alert_type': None}

    def check_vix(self):
        """
        VIX (변동성 지수) 체크

        Returns:
            dict: {
                'vix': float,
                'alert': bool
            }
        """
        try:
            df = self.vix.history(period='1d')

            if df.empty:
                return {'vix': 0, 'alert': False}

            vix_value = df['Close'].iloc[-1]
            alert = vix_value >= self.VIX_THRESHOLD

            return {
                'vix': vix_value,
                'alert': alert
            }

        except Exception as e:
            print(f"[ERROR] VIX 체크 실패: {e}")
            return {'vix': 0, 'alert': False}

    def check_news_sentiment_change(self, tickers):
        """
        주요 종목 뉴스 감성 급변 체크

        Args:
            tickers: 체크할 티커 리스트

        Returns:
            dict: {
                'alerts': [{'ticker': 'AAPL', 'change': 0.5, ...}],
                'has_alert': bool
            }
        """
        alerts = []

        for ticker in tickers:
            try:
                analyzer = NewsSentimentAnalyzer(ticker)
                result = analyzer.calculate_news_score()

                news_count = result.get('news_count', 0)
                avg_sentiment = result.get('avg_sentiment', 0)

                # 뉴스가 충분하고 감성이 극단적인 경우
                if news_count >= 5:
                    if avg_sentiment <= -0.3:  # 매우 부정적
                        alerts.append({
                            'ticker': ticker,
                            'sentiment': avg_sentiment,
                            'type': 'negative',
                            'news_count': news_count
                        })
                    elif avg_sentiment >= 0.5:  # 매우 긍정적
                        alerts.append({
                            'ticker': ticker,
                            'sentiment': avg_sentiment,
                            'type': 'positive',
                            'news_count': news_count
                        })

            except:
                continue

        return {
            'alerts': alerts,
            'has_alert': len(alerts) > 0
        }

    def run_full_check(self, monitored_tickers=None):
        """
        전체 시장 체크 실행

        Args:
            monitored_tickers: 모니터링할 티커 리스트 (None이면 S&P500 주요 종목)

        Returns:
            dict: 모든 체크 결과
        """
        if monitored_tickers is None:
            # S&P500 주요 종목 (시총 상위)
            monitored_tickers = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA',
                'META', 'TSLA', 'BRK-B', 'JPM', 'V'
            ]

        print("=" * 60)
        print("         시장 급변 감지 실행")
        print("=" * 60)
        print()

        # 1. S&P500 체크
        print("[1] S&P500 지수 체크...")
        spy_result = self.check_spy_change()
        print(f"    변화: {spy_result['change_pct']:+.2f}%")

        if spy_result['alert']:
            print(f"    ⚠️ 알림: {spy_result['alert_type']}")

        # 2. VIX 체크
        print()
        print("[2] VIX 변동성 체크...")
        vix_result = self.check_vix()
        print(f"    VIX: {vix_result['vix']:.1f}")

        if vix_result['alert']:
            print(f"    ⚠️ 알림: 변동성 급증")

        # 3. 뉴스 감성 체크
        print()
        print("[3] 주요 종목 뉴스 감성 체크...")
        news_result = self.check_news_sentiment_change(monitored_tickers[:5])

        if news_result['has_alert']:
            print(f"    ⚠️ {len(news_result['alerts'])}개 종목 감성 급변")
            for alert in news_result['alerts']:
                print(f"       {alert['ticker']}: {alert['type']} ({alert['sentiment']:.2f})")
        else:
            print(f"    정상")

        # 종합 판단
        print()
        print("=" * 60)

        has_any_alert = (
            spy_result['alert'] or
            vix_result['alert'] or
            news_result['has_alert']
        )

        if has_any_alert:
            print("🚨 시장 급변 감지! 텔레그램 알림 전송 필요")
        else:
            print("✅ 시장 정상")

        print("=" * 60)

        return {
            'spy': spy_result,
            'vix': vix_result,
            'news': news_result,
            'has_alert': has_any_alert,
            'timestamp': datetime.now()
        }

    def get_recommended_action(self, check_result):
        """
        상황에 따른 권장 조치 생성

        Args:
            check_result: run_full_check() 결과

        Returns:
            str: 권장 조치 설명
        """
        spy = check_result['spy']
        vix = check_result['vix']

        # 급락 상황
        if spy['alert_type'] == 'crash':
            if vix['vix'] > 30:
                return (
                    "⚠️ 급락 + 고변동성\n"
                    "- 방어주 비중 확대 고려\n"
                    "- 현금 보유 비율 증가\n"
                    "- 리밸런싱 연기 권장"
                )
            else:
                return (
                    "📉 일시적 조정 가능성\n"
                    "- 기술적 분석 재확인\n"
                    "- 저점 매수 기회 탐색\n"
                    "- 리밸런싱 진행 가능"
                )

        # 급등 상황
        elif spy['alert_type'] == 'surge':
            return (
                "📈 급등 상황\n"
                "- 수익 실현 검토\n"
                "- 과열 종목 정리\n"
                "- 리밸런싱 조기 실행 고려"
            )

        # 고변동성
        elif vix['alert']:
            return (
                "⚠️ 변동성 급증\n"
                "- 리스크 관리 강화\n"
                "- 손절매 라인 체크\n"
                "- 신규 진입 보수적 접근"
            )

        else:
            return (
                "✅ 정상 범위\n"
                "- 기존 전략 유지\n"
                "- 정기 리밸런싱 진행"
            )


if __name__ == '__main__':
    # 시장 모니터링 실행
    monitor = MarketMonitor()
    result = monitor.run_full_check()

    print()
    print("=" * 60)
    print("권장 조치:")
    print("=" * 60)
    print(monitor.get_recommended_action(result))
    print()
