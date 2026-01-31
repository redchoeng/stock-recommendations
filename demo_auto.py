"""
전체 기능 데모 - 자동 실행 버전 (입력 대기 없음)
pandas-ta 없이 직접 구현한 지표로 완전한 분석
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, '.')

from quant_trading.technical_analyzer_v2 import TechnicalAnalyzerV2
from quant_trading.theme_analyzer import ThemeAnalyzer


def analyze_stock_full(ticker, period='6mo', show_detail=False):
    """
    전체 기능을 활용한 종목 분석

    Args:
        ticker: 종목 티커
        period: 분석 기간
        show_detail: 상세 정보 출력 여부

    Returns:
        dict: 분석 결과
    """
    try:
        # 데이터 다운로드
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty or len(df) < 120:
            if show_detail:
                print(f"[SKIP] {ticker}: Data insufficient")
            return None

        # 1. 기술적 분석 (전체 기능)
        tech_analyzer = TechnicalAnalyzerV2(df)
        tech_result = tech_analyzer.calculate_total_score()

        # 2. 테마 분석
        theme_analyzer = ThemeAnalyzer(ticker)
        theme_result = theme_analyzer.calculate_total_score()

        # 3. 종목 정보
        info = stock.info
        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change_pct = ((current_price - prev_close) / prev_close) * 100

        # 4. 총점 계산
        total_score = tech_result['total_score'] + theme_result['total_score']

        # 5. 시그널 타입 결합
        signal_parts = []
        if tech_result['signals'] != '시그널 없음':
            signal_parts.append(tech_result['signals'])
        if theme_result['matched_theme'] != '미분류':
            signal_parts.append(f"Theme: {theme_result['matched_theme']}")

        signal_type = ' | '.join(signal_parts) if signal_parts else 'No Signal'

        result = {
            'Ticker': ticker,
            'Name': name,
            'Sector': sector,
            'Industry': industry,
            'Price': current_price,
            'Change%': change_pct,
            'Total_Score': total_score,
            'Tech_Score': tech_result['total_score'],
            'Theme_Score': theme_result['total_score'],
            'Signal_Type': signal_type,
            'Theme': theme_result['matched_theme'],

            # 세부 기술적 점수
            'MA_Score': tech_result['ma_score'],
            'Ichimoku_Score': tech_result['ichimoku_score'],
            'Channel_Score': tech_result['channel_score'],
            'Stoch_Score': tech_result['stoch_score'],
            'RSI_Score': tech_result['rsi_score'],

            # 테마 세부
            'Positive_News': theme_result['positive_news'],
        }

        if show_detail:
            print(f"\n{'='*70}")
            print(f"Stock Analysis: {ticker}")
            print(f"{'='*70}")
            print(f"Name: {name}")
            print(f"Sector: {sector}")
            print(f"Industry: {industry}")
            print(f"Price: ${current_price:.2f} ({change_pct:+.2f}%)")

            print(f"\nScore (Total 100 points):")
            print(f"  Total: {total_score}/100")
            print(f"  Technical: {tech_result['total_score']}/75")
            print(f"    - Moving Averages: {tech_result['ma_score']}/15")
            print(f"    - Ichimoku Cloud: {tech_result['ichimoku_score']}/20")
            print(f"    - Channels: {tech_result['channel_score']}/10")
            print(f"    - Stochastic: {tech_result['stoch_score']}/15")
            print(f"    - RSI: {tech_result['rsi_score']}/15")
            print(f"  Theme: {theme_result['total_score']}/25")

            print(f"\nSignal: {signal_type}")
            print(f"Theme: {theme_result['matched_theme']}")
            if theme_result['positive_news'] > 0:
                print(f"Positive News: {theme_result['positive_news']} articles")

            if total_score >= 80:
                print("\n[BUY] Strong Buy! ***")
            elif total_score >= 70:
                print("\n[WATCH] Watch List **")
            elif total_score >= 60:
                print("\n[HOLD] Hold/Monitor *")
            else:
                print("\n[PASS] Pass")

        return result

    except Exception as e:
        if show_detail:
            print(f"[ERROR] {ticker} Analysis failed: {e}")
        return None


def main():
    """메인 함수"""
    print("\n" + "="*70)
    print(" "*15 + "FULL FEATURE DEMO")
    print(" "*10 + "Complete Technical Analysis System")
    print("="*70)
    print("\n[INFO] Using all technical indicators:")
    print("  - Moving Averages (SMA, EMA)")
    print("  - Ichimoku Cloud")
    print("  - Bollinger Bands")
    print("  - Stochastic Oscillator (Multi-timeframe)")
    print("  - RSI with Divergence Detection")
    print("  - MACD, ATR, OBV")
    print("\n[INFO] No pandas-ta required - Pure pandas/numpy implementation")

    try:
        # Demo 1: 개별 종목 상세 분석
        print("\n\n" + "="*70)
        print("DEMO 1: Individual Stock Detailed Analysis")
        print("="*70)

        tickers_detail = ['XOM', 'NVDA', 'LMT']
        for ticker in tickers_detail:
            print(f"\n[Analyzing {ticker}...]")
            analyze_stock_full(ticker, period='1y', show_detail=True)

        # Demo 2: 섹터별 비교
        print("\n\n" + "="*70)
        print("DEMO 2: Sector Comparison Analysis")
        print("="*70)

        sectors = {
            'Energy': ['XOM', 'CVX', 'COP'],
            'Defense': ['LMT', 'RTX', 'NOC'],
            'AI/Tech': ['NVDA', 'AMD', 'AVGO'],
            'Finance': ['JPM', 'BAC', 'GS']
        }

        all_results = []

        for sector_name, tickers in sectors.items():
            print(f"\n[{sector_name} Sector]")
            for ticker in tickers:
                print(f"  {ticker}... ", end='', flush=True)
                result = analyze_stock_full(ticker, show_detail=False)
                if result:
                    all_results.append(result)
                    print(f"Score: {result['Total_Score']}")
                else:
                    print("Failed")

        # 결과 정리
        if all_results:
            df = pd.DataFrame(all_results)
            df = df.sort_values('Total_Score', ascending=False)

            print(f"\n{'='*70}")
            print("Sector Analysis Results")
            print(f"{'='*70}\n")

            cols = ['Ticker', 'Name', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Theme']
            print(df[cols].to_string(index=False))

            # 섹터별 평균
            print(f"\n{'='*70}")
            print("Sector Average Scores")
            print(f"{'='*70}")

            sector_avg = df.groupby('Theme')['Total_Score'].agg(['count', 'mean', 'max'])
            print(sector_avg)

        # Demo 3: 추천 종목
        print("\n\n" + "="*70)
        print("DEMO 3: Stock Recommendations (70+ points)")
        print("="*70)

        # 주요 종목 리스트
        tickers = [
            # 에너지
            'XOM', 'CVX', 'COP', 'SLB', 'EOG',
            # 방산
            'LMT', 'RTX', 'NOC', 'GD', 'BA',
            # AI/기술
            'NVDA', 'AMD', 'AVGO', 'MSFT', 'GOOGL',
            # 금융
            'JPM', 'BAC', 'WFC', 'GS',
            # 기타
            'AAPL', 'TSLA', 'META'
        ]

        print(f"\nAnalyzing {len(tickers)} stocks...\n")

        results = []
        for idx, ticker in enumerate(tickers, 1):
            print(f"[{idx}/{len(tickers)}] {ticker:6s} ... ", end='', flush=True)
            result = analyze_stock_full(ticker, period='6mo', show_detail=False)
            if result:
                results.append(result)
                print(f"Score: {result['Total_Score']:3.0f}")
            else:
                print("Failed")

        if results:
            df = pd.DataFrame(results)
            df = df.sort_values('Total_Score', ascending=False)

            # 전체 결과
            print(f"\n{'='*70}")
            print("Overall Analysis Results (Sorted by Score)")
            print(f"{'='*70}\n")

            cols = ['Ticker', 'Name', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Signal_Type']
            print(df[cols].head(10).to_string(index=False))

            # 추천 종목 (70점 이상)
            recommendations = df[df['Total_Score'] >= 70]

            print(f"\n\n{'='*70}")
            print(f"BUY RECOMMENDATIONS (70+ points): {len(recommendations)} stocks")
            print(f"{'='*70}\n")

            if not recommendations.empty:
                detail_cols = ['Ticker', 'Name', 'Total_Score', 'MA_Score', 'Ichimoku_Score',
                              'Channel_Score', 'Stoch_Score', 'RSI_Score', 'Theme_Score']
                print(recommendations[detail_cols].to_string(index=False))

                # CSV 저장
                filename = f"recommendations_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                recommendations.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"\n[SAVED] {filename}")
            else:
                print("No stocks scored 70+ points in current market conditions.")
                print("TOP 5 stocks:")
                print(df[['Ticker', 'Name', 'Total_Score', 'Signal_Type']].head(5).to_string(index=False))

        print("\n\n" + "="*70)
        print("All demos completed!")
        print("="*70)
        print("\nAvailable tools:")
        print("  1. demo_auto.py              - This script (auto-run, no input)")
        print("  2. demo_full_features.py     - Interactive version")
        print("  3. demo_quant_interactive.py - Interactive menu")
        print("  4. run_all_demos.py          - Automated sector demos")

    except KeyboardInterrupt:
        print("\n\n[EXIT] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
