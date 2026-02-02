"""
퀀트 전략 백테스팅 시스템
과거 데이터로 전략 성과 검증
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


class StrategyBacktest:
    """전략 백테스팅 클래스"""

    def __init__(self, start_date, end_date, initial_capital=100000, top_n=10, rebalance_days=7):
        """
        초기화

        Args:
            start_date: 백테스트 시작일
            end_date: 백테스트 종료일
            initial_capital: 초기 자본금 (달러)
            top_n: 포트폴리오 종목 수
            rebalance_days: 리밸런싱 주기 (일)
        """
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        self.top_n = top_n
        self.rebalance_days = rebalance_days
        self.capital = initial_capital

        # 결과 저장
        self.portfolio_history = []
        self.trade_history = []
        self.daily_returns = []

    def get_sp500_tickers(self, limit=100):
        """S&P500 종목 가져오기 (상위 100개만)"""
        print("📊 S&P500 종목 리스트 가져오는 중...")

        # 주요 종목만 (더 빠르게)
        major_tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
            'UNH', 'JNJ', 'V', 'XOM', 'WMT', 'JPM', 'MA', 'PG', 'CVX', 'HD',
            'LLY', 'ABBV', 'MRK', 'KO', 'PEP', 'AVGO', 'COST', 'TMO', 'MCD',
            'CSCO', 'ACN', 'ABT', 'DHR', 'ADBE', 'TXN', 'NKE', 'NEE', 'WFC',
            'BAC', 'DIS', 'PM', 'COP', 'AMD', 'VZ', 'CMCSA', 'LIN', 'NFLX',
            'INTC', 'RTX', 'BMY', 'UPS', 'T', 'QCOM', 'HON', 'LOW', 'SPGI',
            'AMGN', 'UNP', 'INTU', 'BA', 'CAT', 'GE', 'DE', 'SBUX', 'GILD',
            'AXP', 'BLK', 'MDT', 'PLD', 'AMT', 'TJX', 'SYK', 'SCHW', 'MMM',
            'ADP', 'BKNG', 'MDLZ', 'C', 'CB', 'TMUS', 'CVS', 'ZTS', 'ADI',
            'MO', 'ISRG', 'CI', 'SO', 'DUK', 'PNC', 'TGT', 'USB', 'BDX', 'EOG',
            'REGN', 'NOC', 'MMC', 'SLB', 'HUM', 'ETN', 'CL', 'ITW', 'GD'
        ]

        return major_tickers[:limit]

    def analyze_stock(self, ticker, date):
        """특정 날짜의 종목 분석"""
        try:
            # 해당 날짜까지의 데이터 가져오기 (2년치)
            stock = yf.Ticker(ticker)
            start_fetch = date - timedelta(days=730)  # 2년
            df = stock.history(start=start_fetch, end=date)

            if df.empty or len(df) < 180:
                return None

            # 기술적 분석
            tech_v3 = TechnicalAnalyzerV3(df)
            result_v3 = tech_v3.calculate_total_score()

            # 테마 분석 (간소화 - 시간 절약)
            theme_score = 0
            try:
                theme_analyzer = ThemeAnalyzer(ticker)
                theme_result = theme_analyzer.calculate_total_score()
                theme_score = theme_result['total_score']
            except:
                theme_score = 0  # 테마 분석 실패 시 0점

            total_score = result_v3['total_score'] + theme_score

            return {
                'ticker': ticker,
                'date': date,
                'total_score': total_score,
                'tech_score': result_v3['total_score'],
                'theme_score': theme_score,
                'close_price': df['Close'].iloc[-1]
            }

        except Exception as e:
            print(f"  ⚠️  {ticker} 분석 실패: {e}")
            return None

    def get_top_stocks(self, date, tickers, max_workers=10):
        """특정 날짜의 상위 종목 선정"""
        print(f"\n📅 {date.strftime('%Y-%m-%d')} 종목 분석 중...")

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.analyze_stock, ticker, date): ticker
                      for ticker in tickers}

            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 20 == 0:
                    print(f"  진행률: {completed}/{len(tickers)}")

                result = future.result()
                if result:
                    results.append(result)

        # 점수순 정렬
        results.sort(key=lambda x: x['total_score'], reverse=True)

        print(f"✅ 분석 완료: {len(results)}개 종목")
        if results:
            print(f"   최고 점수: {results[0]['ticker']} ({results[0]['total_score']:.0f}점)")

        return results[:self.top_n]

    def calculate_portfolio_return(self, portfolio, next_date):
        """포트폴리오 수익률 계산"""
        total_return = 0

        for stock in portfolio:
            ticker = stock['ticker']
            buy_price = stock['close_price']

            try:
                # 다음 리밸런싱 날짜의 가격 가져오기
                stock_data = yf.Ticker(ticker)
                df = stock_data.history(start=next_date - timedelta(days=5),
                                       end=next_date + timedelta(days=1))

                if not df.empty:
                    sell_price = df['Close'].iloc[-1]
                    stock_return = (sell_price - buy_price) / buy_price
                    total_return += stock_return / len(portfolio)  # 동일 비중
                else:
                    # 데이터 없으면 0% 수익
                    pass

            except Exception as e:
                print(f"  ⚠️  {ticker} 수익률 계산 실패: {e}")

        return total_return

    def run_backtest(self):
        """백테스팅 실행"""
        print("=" * 60)
        print("🚀 퀀트 전략 백테스팅 시작")
        print("=" * 60)
        print(f"기간: {self.start_date.strftime('%Y-%m-%d')} ~ {self.end_date.strftime('%Y-%m-%d')}")
        print(f"초기 자본: ${self.initial_capital:,.0f}")
        print(f"포트폴리오: 상위 {self.top_n}개 종목")
        print(f"리밸런싱: {self.rebalance_days}일마다")
        print("=" * 60)

        # S&P500 종목 리스트
        tickers = self.get_sp500_tickers()

        # 리밸런싱 날짜 생성
        current_date = self.start_date
        rebalance_dates = []

        while current_date <= self.end_date:
            rebalance_dates.append(current_date)
            current_date += timedelta(days=self.rebalance_days)

        print(f"\n📅 총 리밸런싱 횟수: {len(rebalance_dates)}회")

        # 각 리밸런싱 날짜마다 실행
        for i, date in enumerate(rebalance_dates[:-1]):
            print(f"\n{'='*60}")
            print(f"🔄 리밸런싱 #{i+1}/{len(rebalance_dates)-1}")

            # 상위 종목 선정
            top_stocks = self.get_top_stocks(date, tickers)

            if not top_stocks:
                print("⚠️  선정된 종목 없음, 건너뜀")
                continue

            # 다음 리밸런싱까지 수익률 계산
            next_date = rebalance_dates[i + 1]
            portfolio_return = self.calculate_portfolio_return(top_stocks, next_date)

            # 자본 업데이트
            old_capital = self.capital
            self.capital = self.capital * (1 + portfolio_return)

            # 기록
            self.portfolio_history.append({
                'date': date,
                'capital': self.capital,
                'return': portfolio_return,
                'top_stocks': [s['ticker'] for s in top_stocks],
                'top_scores': [s['total_score'] for s in top_stocks]
            })

            print(f"\n📊 포트폴리오: {', '.join([s['ticker'] for s in top_stocks[:5]])}")
            print(f"💰 수익률: {portfolio_return*100:+.2f}%")
            print(f"💵 자본: ${old_capital:,.0f} → ${self.capital:,.0f}")

        return self.generate_report()

    def generate_report(self):
        """백테스팅 결과 리포트 생성"""
        if not self.portfolio_history:
            return None

        print("\n" + "="*60)
        print("📊 백테스팅 결과 리포트")
        print("="*60)

        # 총 수익률
        total_return = (self.capital - self.initial_capital) / self.initial_capital

        # 각 기간별 수익률
        returns = [p['return'] for p in self.portfolio_history]

        # 통계
        avg_return = np.mean(returns) if returns else 0
        std_return = np.std(returns) if returns else 0
        sharpe = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0

        # 최대 낙폭 (MDD)
        capital_history = [p['capital'] for p in self.portfolio_history]
        peak = capital_history[0]
        max_dd = 0

        for capital in capital_history:
            if capital > peak:
                peak = capital
            dd = (capital - peak) / peak
            if dd < max_dd:
                max_dd = dd

        # 승률
        winning_trades = sum(1 for r in returns if r > 0)
        win_rate = winning_trades / len(returns) if returns else 0

        # 결과 출력
        print(f"\n💰 최종 자본: ${self.capital:,.2f}")
        print(f"📈 총 수익률: {total_return*100:+.2f}%")
        print(f"📊 연평균 수익률: {(total_return / ((self.end_date - self.start_date).days / 365))*100:+.2f}%")
        print(f"🎯 승률: {win_rate*100:.1f}% ({winning_trades}/{len(returns)})")
        print(f"📉 최대 낙폭 (MDD): {max_dd*100:.2f}%")
        print(f"⚡ 샤프 비율: {sharpe:.2f}")
        print(f"📏 평균 수익률: {avg_return*100:+.2f}%")
        print(f"📊 변동성: {std_return*100:.2f}%")

        # 벤치마크 대비
        print(f"\n📊 S&P500 대비 성과")
        try:
            spy = yf.Ticker('SPY')
            spy_data = spy.history(start=self.start_date, end=self.end_date)
            spy_return = (spy_data['Close'].iloc[-1] - spy_data['Close'].iloc[0]) / spy_data['Close'].iloc[0]

            print(f"S&P500 수익률: {spy_return*100:+.2f}%")
            print(f"초과 수익률: {(total_return - spy_return)*100:+.2f}%")

            if total_return > spy_return:
                print("✅ 전략 승리! 🎉")
            else:
                print("❌ S&P500이 더 나음")
        except:
            print("⚠️  벤치마크 데이터 없음")

        print("\n" + "="*60)

        # CSV 저장
        df = pd.DataFrame(self.portfolio_history)
        filename = f"backtest_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"📁 결과 저장: {filename}")

        return {
            'final_capital': self.capital,
            'total_return': total_return,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_dd,
            'avg_return': avg_return,
            'std_return': std_return
        }


if __name__ == '__main__':
    print("""
    ============================================================
              퀀트 전략 백테스팅 시스템
           과거 데이터로 전략 성과 검증
    ============================================================
    """)

    # 사용자 입력
    print("\n백테스팅 설정:")
    print("-" * 60)

    # 기간 설정
    period = input("백테스팅 기간 (1=3개월, 2=6개월, 3=1년, 4=2년) [기본: 3]: ").strip()

    end_date = datetime.now()
    if period == '1':
        start_date = end_date - timedelta(days=90)
        print("✅ 3개월 백테스팅")
    elif period == '2':
        start_date = end_date - timedelta(days=180)
        print("✅ 6개월 백테스팅")
    elif period == '4':
        start_date = end_date - timedelta(days=730)
        print("✅ 2년 백테스팅")
    else:
        start_date = end_date - timedelta(days=365)
        print("✅ 1년 백테스팅 (추천)")

    # 초기 자본
    capital_input = input("초기 자본 (달러) [기본: 100000]: ").strip()
    initial_capital = int(capital_input) if capital_input else 100000

    # 포트폴리오 크기
    top_n_input = input("포트폴리오 종목 수 [기본: 10]: ").strip()
    top_n = int(top_n_input) if top_n_input else 10

    # 리밸런싱 주기
    rebalance_input = input("리밸런싱 주기 (일) [기본: 7]: ").strip()
    rebalance_days = int(rebalance_input) if rebalance_input else 7

    print("\n" + "="*60)
    input("⏎ 엔터를 눌러 백테스팅 시작...")

    # 백테스팅 실행
    backtest = StrategyBacktest(
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital,
        top_n=top_n,
        rebalance_days=rebalance_days
    )

    result = backtest.run_backtest()

    print("\n🎉 백테스팅 완료!")
    print("\n💡 Tip: CSV 파일을 열어서 상세 내역을 확인하세요!")
