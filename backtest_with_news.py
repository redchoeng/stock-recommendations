"""
뉴스 감성 분석을 포함한 백테스팅
StockNews 방식 적용 - 미국 주식

총점 시스템:
- 기술적 분석: 75점 (기존)
- 뉴스 감성: 20점 (NEW)
- 테마 분석: 5점 (간소화)
= 총 100점
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import time
sys.path.insert(0, '.')

from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3
from quant_trading.news_sentiment_analyzer import NewsSentimentAnalyzer

print("=" * 60)
print("   NEWS SENTIMENT 전략 백테스팅")
print("=" * 60)
print()
print("개선사항:")
print("  - 뉴스 감성 분석 추가 (20점)")
print("  - 최근 7일 뉴스 분석")
print("  - TextBlob 감성 분석")
print("  - 기간: 1년")
print("=" * 60)
print()

# 설정
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
initial_capital = 100000
top_n = 10
rebalance_days = 7

# 주요 종목
major_tickers = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
    'UNH', 'JNJ', 'V', 'XOM', 'WMT', 'JPM', 'MA', 'PG', 'CVX', 'HD',
    'LLY', 'ABBV', 'MRK', 'KO', 'PEP', 'AVGO', 'COST', 'TMO', 'MCD',
    'CSCO', 'ACN', 'ABT', 'DHR', 'ADBE', 'TXN', 'NKE', 'NEE', 'WFC',
    'BAC', 'DIS', 'PM', 'COP', 'AMD', 'VZ', 'CMCSA', 'LIN', 'NFLX',
    'INTC', 'RTX', 'BMY', 'UPS', 'T'
]

print(f"분석 종목: {len(major_tickers)}개")
print()


def analyze_stock(ticker, date):
    """
    종목 분석 (뉴스 감성 포함)

    API 제한 대응:
    - 뉴스 분석 실패 시 0점 처리
    - 최소 1초 대기
    """
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
        try:
            news_analyzer = NewsSentimentAnalyzer(ticker)
            news_result = news_analyzer.calculate_news_score()
            news_score = news_result['total_score']
            time.sleep(1)  # API 제한 대응
        except Exception as e:
            # 뉴스 분석 실패 시 0점
            news_score = 0

        # 3. 테마 분석 (5점, 간소화)
        theme_score = 0

        # 총점 (100점)
        total_score = tech_score + news_score + theme_score

        return {
            'ticker': ticker,
            'date': date,
            'total_score': total_score,
            'tech_score': tech_score,
            'news_score': news_score,
            'theme_score': theme_score,
            'close_price': df['Close'].iloc[-1]
        }

    except Exception as e:
        return None


def get_top_stocks(date, tickers):
    """상위 종목 선정"""
    results = []

    # 순차 처리 (API 제한 방지)
    for ticker in tickers:
        result = analyze_stock(ticker, date)
        if result:
            results.append(result)

    # 점수순 정렬
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results[:top_n]


def calculate_return(portfolio, next_date):
    """수익률 계산"""
    total_return = 0

    for stock in portfolio:
        ticker = stock['ticker']
        buy_price = stock['close_price']

        try:
            stock_data = yf.Ticker(ticker)
            df = stock_data.history(start=next_date - timedelta(days=5),
                                   end=next_date + timedelta(days=1))

            if not df.empty:
                sell_price = df['Close'].iloc[-1]
                stock_return = (sell_price - buy_price) / buy_price
                total_return += stock_return / len(portfolio)

        except:
            pass

    return total_return


# 백테스팅 실행
print("백테스팅 시작...")
print("주의: 뉴스 분석으로 인해 시간이 오래 걸립니다 (종목당 1초)")
print()

capital = initial_capital
portfolio_history = []

# 리밸런싱 날짜
current_date = start_date
rebalance_dates = []

while current_date <= end_date:
    rebalance_dates.append(current_date)
    current_date += timedelta(days=rebalance_days)

print(f"총 {len(rebalance_dates)-1}회 리밸런싱")
print()

# 각 리밸런싱
for i, date in enumerate(rebalance_dates[:-1]):
    print(f"[{i+1}/{len(rebalance_dates)-1}] {date.strftime('%Y-%m-%d')}")

    # 상위 종목 선정
    top_stocks = get_top_stocks(date, major_tickers)

    if not top_stocks:
        print("  -> No stocks")
        continue

    # 수익률 계산
    next_date = rebalance_dates[i + 1]
    portfolio_return = calculate_return(top_stocks, next_date)

    # 자본 업데이트
    old_capital = capital
    capital = capital * (1 + portfolio_return)

    portfolio_history.append({
        'date': date,
        'capital': capital,
        'return': portfolio_return,
        'top_stocks': [s['ticker'] for s in top_stocks],
        'avg_news_score': np.mean([s['news_score'] for s in top_stocks])
    })

    # 평균 뉴스 점수 표시
    avg_news = np.mean([s['news_score'] for s in top_stocks])
    print(f"  -> {', '.join([s['ticker'] for s in top_stocks[:3]])}...")
    print(f"  -> News: {avg_news:.1f}/20 | Return: {portfolio_return*100:+.2f}% | ${capital:,.0f}")

# 결과
print()
print("=" * 60)
print("   NEWS SENTIMENT 전략 백테스팅 결과")
print("=" * 60)
print()

total_return = (capital - initial_capital) / initial_capital
returns = [p['return'] for p in portfolio_history]

avg_return = np.mean(returns)
std_return = np.std(returns)
sharpe = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0

winning_trades = sum(1 for r in returns if r > 0)
win_rate = winning_trades / len(returns) if returns else 0

# MDD
capital_history = [p['capital'] for p in portfolio_history]
peak = capital_history[0]
max_dd = 0

for cap in capital_history:
    if cap > peak:
        peak = cap
    dd = (cap - peak) / peak
    if dd < max_dd:
        max_dd = dd

# 평균 뉴스 점수
avg_news = np.mean([p['avg_news_score'] for p in portfolio_history])

print(f"최종 자본:         ${capital:,.2f}")
print(f"총 수익률:         {total_return*100:+.2f}%")
print(f"연평균 수익률:     {total_return*100:+.2f}%")
print(f"승률:             {win_rate*100:.1f}% ({winning_trades}/{len(returns)})") print(f"최대 낙폭:         {max_dd*100:.2f}%")
print(f"샤프 비율:         {sharpe:.2f}")
print(f"평균 뉴스 점수:    {avg_news:.1f}/20점")
print()

# S&P500 대비
try:
    spy = yf.Ticker('SPY')
    spy_data = spy.history(start=start_date, end=end_date)
    spy_return = (spy_data['Close'].iloc[-1] - spy_data['Close'].iloc[0]) / spy_data['Close'].iloc[0]

    print(f"S&P500 수익률:     {spy_return*100:+.2f}%")
    print(f"초과 수익률:       {(total_return - spy_return)*100:+.2f}%")
    print()

    if total_return > spy_return:
        print("결과: NEWS SENTIMENT 전략 승리!")
    else:
        print("결과: S&P500이 더 나음")
except:
    print("S&P500 비교 실패")

print()
print("=" * 60)

# CSV 저장
df = pd.DataFrame(portfolio_history)
filename = f"backtest_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(filename, index=False)
print(f"결과 저장: {filename}")
print()
