"""
개선된 퀀트 전략 백테스팅
- Value 전략 추가 (20점)
- 섹터 분산 강화
- 1년 백테스팅
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
sys.path.insert(0, '.')

from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3
from quant_trading.theme_analyzer import ThemeAnalyzer

print("=" * 60)
print("   IMPROVED 전략 백테스팅 (Value 추가)")
print("=" * 60)
print()
print("개선사항:")
print("  - Value 전략 추가 (P/E, P/B, 배당, PEG)")
print("  - 섹터 분산 강화")
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


def calculate_value_score(ticker):
    """
    Value 점수 계산 (20점)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        score = 0

        # 1. P/E Ratio
        pe = info.get('trailingPE', 999)
        if pe < 15:
            score += 5
        elif pe < 20:
            score += 3

        # 2. P/B Ratio
        pb = info.get('priceToBook', 999)
        if pb < 2.0:
            score += 5
        elif pb < 3.0:
            score += 3

        # 3. 배당수익률
        div_yield = info.get('dividendYield', 0)
        if div_yield > 0.02:  # 2%
            score += 5
        elif div_yield > 0.01:  # 1%
            score += 3

        # 4. PEG Ratio
        peg = info.get('pegRatio', 999)
        if 0 < peg < 1.5:
            score += 5
        elif peg < 2.0:
            score += 3

        return score

    except:
        return 0


def analyze_stock(ticker, date):
    """종목 분석 (Value 추가)"""
    try:
        stock = yf.Ticker(ticker)
        start_fetch = date - timedelta(days=730)
        df = stock.history(start=start_fetch, end=date)

        if df.empty or len(df) < 180:
            return None

        # 기술적 분석
        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()

        # 테마 분석 (간소화)
        theme_score = 0

        # Value 분석 (NEW!)
        value_score = calculate_value_score(ticker)

        # 총점 (120점 만점)
        total_score = result_v3['total_score'] + theme_score + value_score

        # 섹터 정보
        info = stock.info
        sector = info.get('sector', 'Unknown')

        return {
            'ticker': ticker,
            'date': date,
            'total_score': total_score,
            'tech_score': result_v3['total_score'],
            'value_score': value_score,
            'sector': sector,
            'close_price': df['Close'].iloc[-1]
        }

    except Exception as e:
        return None


def enforce_sector_limits(candidates, top_n=10):
    """
    섹터 분산 강화
    """
    SECTOR_LIMITS = {
        'Financials': 0.25,
        'Technology': 0.30,
        'Healthcare': 0.25,
        'Consumer Cyclical': 0.20,
        'Consumer Defensive': 0.20,
        'Energy': 0.20,
    }

    portfolio = []
    sector_counts = {}

    for stock in candidates:
        if len(portfolio) >= top_n:
            break

        sector = stock['sector']

        # 현재 섹터 비중
        if portfolio:
            current_ratio = sector_counts.get(sector, 0) / len(portfolio)
            max_ratio = SECTOR_LIMITS.get(sector, 0.20)

            if current_ratio >= max_ratio:
                continue  # 섹터 제한 초과, 스킵

        portfolio.append(stock)
        sector_counts[sector] = sector_counts.get(sector, 0) + 1

    return portfolio


def get_top_stocks(date, tickers):
    """상위 종목 선정 (섹터 분산 적용)"""
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(analyze_stock, ticker, date): ticker
                  for ticker in tickers}

        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    # 점수순 정렬
    results.sort(key=lambda x: x['total_score'], reverse=True)

    # 섹터 분산 적용
    portfolio = enforce_sector_limits(results, top_n)

    return portfolio


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
    print(f"[{i+1}/{len(rebalance_dates)-1}] {date.strftime('%Y-%m-%d')}", end=" ")

    # 상위 종목 선정
    top_stocks = get_top_stocks(date, major_tickers)

    if not top_stocks:
        print("-> No stocks")
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
        'avg_value_score': np.mean([s['value_score'] for s in top_stocks])
    })

    print(f"-> {', '.join([s['ticker'] for s in top_stocks[:3]])}... | {portfolio_return*100:+.2f}% | ${capital:,.0f}")

# 결과
print()
print("=" * 60)
print("   IMPROVED 전략 백테스팅 결과")
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

# 평균 Value 점수
avg_value = np.mean([p['avg_value_score'] for p in portfolio_history])

print(f"최종 자본:         ${capital:,.2f}")
print(f"총 수익률:         {total_return*100:+.2f}%")
print(f"연평균 수익률:     {total_return*100:+.2f}%")
print(f"승률:             {win_rate*100:.1f}% ({winning_trades}/{len(returns)})")
print(f"최대 낙폭:         {max_dd*100:.2f}%")
print(f"샤프 비율:         {sharpe:.2f}")
print(f"평균 Value 점수:   {avg_value:.1f}/20점")
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
        print("결과: IMPROVED 전략 승리! (Value 추가 효과)")
    else:
        print("결과: S&P500이 더 나음")
except:
    print("S&P500 비교 실패")

print()
print("=" * 60)

# CSV 저장
df = pd.DataFrame(portfolio_history)
filename = f"backtest_improved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
df.to_csv(filename, index=False)
print(f"결과 저장: {filename}")
print()

# 비교 결과 로드 (기존 결과와 비교)
try:
    import glob
    old_files = glob.glob("backtest_result_*.csv")
    if old_files:
        old_file = max(old_files)
        df_old = pd.read_csv(old_file)
        old_capital = df_old['capital'].iloc[-1]
        old_return = (old_capital - initial_capital) / initial_capital

        print("=" * 60)
        print("   기존 vs IMPROVED 비교")
        print("=" * 60)
        print()
        print(f"기존 전략:")
        print(f"  수익률: {old_return*100:+.2f}%")
        print(f"  최종 자본: ${old_capital:,.0f}")
        print()
        print(f"IMPROVED 전략 (Value 추가):")
        print(f"  수익률: {total_return*100:+.2f}%")
        print(f"  최종 자본: ${capital:,.0f}")
        print()
        improvement = ((total_return - old_return) / abs(old_return)) * 100
        print(f"개선도: {improvement:+.1f}%")
        print()
except:
    pass
