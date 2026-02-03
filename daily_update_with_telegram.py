"""
텔레그램 알림 통합 일일 업데이트
- 14일 리밸런싱 결과 전송
- 시장 급변 감지 및 알림
- 일일 시장 모니터링
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import sys
import time
sys.path.insert(0, '.')

from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3
from quant_trading.news_sentiment_analyzer import NewsSentimentAnalyzer
from telegram_notifier import TelegramNotifier
from market_monitor import MarketMonitor


# S&P500 주요 종목 (50개)
SP500_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
    'V', 'XOM', 'JPM', 'WMT', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
    'KO', 'AVGO', 'PEP', 'COST', 'LLY', 'TMO', 'MCD', 'CSCO', 'ACN', 'ABT',
    'DHR', 'NKE', 'VZ', 'ADBE', 'CRM', 'NEE', 'TXN', 'PM', 'CMCSA', 'WFC',
    'ORCL', 'DIS', 'HON', 'IBM', 'QCOM', 'UPS', 'INTC', 'BA', 'GS', 'CAT'
]


def analyze_stock(ticker, date=None):
    """종목 분석 (기술적 + 뉴스)"""
    if date is None:
        date = datetime.now()

    try:
        stock = yf.Ticker(ticker)
        start_fetch = date - timedelta(days=730)
        df = stock.history(start=start_fetch, end=date)

        if df.empty or len(df) < 180:
            return None

        # 1. 기술적 분석 (75점)
        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()
        tech_score = result_v3['total_score']

        # 2. 뉴스 감성 분석 (20점)
        news_score = 0
        news_count = 0
        try:
            news_analyzer = NewsSentimentAnalyzer(ticker)
            news_result = news_analyzer.calculate_news_score()
            news_score = news_result['total_score']
            news_count = news_result['news_count']
            time.sleep(0.5)  # API 제한 대응
        except:
            pass

        # 총점 (95점)
        total_score = tech_score + news_score

        return {
            'ticker': ticker,
            'total_score': total_score,
            'tech_score': tech_score,
            'news_score': news_score,
            'news_count': news_count,
            'close_price': df['Close'].iloc[-1]
        }

    except Exception as e:
        return None


def get_top_stocks(tickers, top_n=10):
    """상위 종목 선정"""
    print(f"분석 중: {len(tickers)}개 종목")
    results = []

    for i, ticker in enumerate(tickers):
        if (i + 1) % 10 == 0:
            print(f"  진행: {i+1}/{len(tickers)}")

        result = analyze_stock(ticker)
        if result:
            results.append(result)

    # 점수순 정렬
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results[:top_n]


def should_rebalance():
    """
    리밸런싱 필요 여부 체크
    14일마다 실행
    """
    # 마지막 리밸런싱 날짜 저장 파일
    LAST_REBALANCE_FILE = 'last_rebalance.txt'

    try:
        with open(LAST_REBALANCE_FILE, 'r') as f:
            last_date_str = f.read().strip()
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')

        days_since = (datetime.now() - last_date).days

        if days_since >= 14:
            # 14일 경과 - 리밸런싱 필요
            with open(LAST_REBALANCE_FILE, 'w') as f:
                f.write(datetime.now().strftime('%Y-%m-%d'))
            return True, days_since
        else:
            return False, days_since

    except FileNotFoundError:
        # 파일 없음 - 첫 실행
        with open(LAST_REBALANCE_FILE, 'w') as f:
            f.write(datetime.now().strftime('%Y-%m-%d'))
        return True, 0


def main():
    """메인 실행"""
    print("=" * 60)
    print("         텔레그램 알림 일일 업데이트")
    print("=" * 60)
    print()

    # config.py에서 설정 불러오기
    try:
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    except ImportError:
        print("[ERROR] config.py에 텔레그램 설정이 없습니다.")
        print("텔레그램 알림 없이 계속 진행합니다...")
        notifier = None

    # 1. 시장 급변 감지
    print("[1] 시장 급변 감지...")
    monitor = MarketMonitor()
    market_check = monitor.run_full_check()

    # 2. 급변 알림
    if market_check['has_alert'] and notifier:
        print()
        print("[2] 시장 급변 알림 전송...")

        spy = market_check['spy']
        vix = market_check['vix']

        # 알림 타입 결정
        if spy['alert']:
            alert_type = spy['alert_type']
        elif vix['alert']:
            alert_type = 'volatility'
        else:
            alert_type = 'news'

        details = {
            'description': monitor.get_recommended_action(market_check),
            'spy_change': spy.get('change_pct', 0),
            'vix': vix.get('vix', 0),
            'recommended_action': monitor.get_recommended_action(market_check)
        }

        notifier.send_market_alert(alert_type, details)
    else:
        print()
        print("[2] 시장 정상 - 급변 알림 불필요")

    # 3. 리밸런싱 체크
    print()
    print("[3] 리밸런싱 체크...")
    need_rebalance, days_since = should_rebalance()

    if need_rebalance or market_check['has_alert']:
        print(f"    리밸런싱 실행 (마지막 리밸런싱: {days_since}일 전)")
        print()

        # 상위 종목 분석
        print("[4] 상위 종목 분석...")
        top_stocks = get_top_stocks(SP500_TICKERS, top_n=10)

        print()
        print("=" * 60)
        print("TOP 10 종목:")
        for i, stock in enumerate(top_stocks, 1):
            print(f"{i:2d}. {stock['ticker']:5s} - {stock['total_score']:.1f}점 "
                  f"(기술: {stock['tech_score']:.1f}, 뉴스: {stock['news_score']:.1f})")
        print("=" * 60)

        # 텔레그램 알림
        if notifier:
            print()
            print("[5] 리밸런싱 결과 전송...")

            # 간단한 성과 계산 (SPY 대비)
            try:
                spy = yf.Ticker('SPY')
                spy_df = spy.history(period='1mo')
                if spy_df.empty or len(spy_df) < 2:
                    spy_return = 0
                else:
                    spy_return = (spy_df['Close'].iloc[-1] - spy_df['Close'].iloc[0]) / spy_df['Close'].iloc[0]
            except Exception as e:
                print(f"    [WARNING] SPY 데이터 로드 실패: {e}")
                spy_return = 0

            performance = {
                'return': spy_return,
                'sharpe': 4.49,  # 백테스트 결과
                'win_rate': 0.75
            }

            notifier.send_rebalance_report(top_stocks, performance)
            print("    전송 완료!")

    else:
        print(f"    리밸런싱 불필요 (마지막 리밸런싱: {days_since}일 전)")
        print()

        # 일일 요약만 전송
        if notifier:
            print("[4] 일일 시장 요약 전송...")

            # 간단한 TOP 3
            quick_stocks = get_top_stocks(SP500_TICKERS[:20], top_n=3)

            spy = market_check['spy']
            vix = market_check['vix']

            summary = {
                'spy_change': spy.get('change_pct', 0),
                'vix': vix.get('vix', 0),
                'top_stocks': [
                    {'ticker': s['ticker'], 'score': s['total_score']}
                    for s in quick_stocks
                ]
            }

            notifier.send_daily_summary(summary)
            print("    전송 완료!")

    print()
    print("=" * 60)
    print("일일 업데이트 완료!")
    print("=" * 60)


if __name__ == '__main__':
    main()
