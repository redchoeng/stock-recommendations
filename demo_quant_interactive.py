"""
퀀트 트레이딩 시스템 - 인터랙티브 메뉴 버전
모든 분석 옵션을 선택할 수 있는 대화형 인터페이스
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys


def simple_technical_score(df):
    """간단한 기술적 분석 점수"""
    score = 0
    signals = []

    # 이동평균선 계산
    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_60'] = df['Close'].rolling(window=60).mean()

    recent = df.iloc[-1]
    prev = df.iloc[-2]

    # 골든크로스
    if prev['SMA_20'] <= prev['SMA_60'] and recent['SMA_20'] > recent['SMA_60']:
        score += 10
        signals.append("Golden Cross")

    # 정배열
    if recent['SMA_5'] > recent['SMA_20'] > recent['SMA_60']:
        score += 5
        signals.append("Alignment")

    # RSI 계산
    try:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        if not pd.isna(prev.get('RSI')) and not pd.isna(recent.get('RSI')):
            # RSI 과매도 탈출
            if prev['RSI'] <= 30 and recent['RSI'] > 30:
                score += 10
                signals.append("RSI Oversold Exit")
            # RSI 과열 경고
            elif recent['RSI'] >= 70:
                signals.append("RSI Overbought (Warning)")
    except:
        pass

    # 상승 추세
    if df['Close'].iloc[-5:].is_monotonic_increasing:
        score += 5
        signals.append("Uptrend")

    # 거래량 급증
    if recent['Volume'] > df['Volume'].iloc[-10:-1].mean() * 1.5:
        score += 5
        signals.append("Volume Surge")

    return score, ' + '.join(signals) if signals else 'No Signal'


def get_theme_score(sector, industry):
    """테마 점수 계산"""
    theme_score = 0
    matched_theme = 'None'

    # 트럼프 정책 수혜 섹터
    themes = {
        'Energy': ['Energy', 'Oil', 'Gas'],
        'Defense': ['Defense', 'Aerospace'],
        'AI/Tech': ['Technology', 'Semiconductor', 'Software'],
        'Finance': ['Financial', 'Bank'],
        'Nuclear': ['Utilities', 'Nuclear']
    }

    for theme_name, keywords in themes.items():
        if any(kw in sector for kw in keywords) or any(kw in industry for kw in keywords):
            theme_score = 25
            matched_theme = theme_name
            break

    return theme_score, matched_theme


def analyze_stock_detailed(ticker, period='6mo', show_detail=False):
    """종목 상세 분석"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty or len(df) < 60:
            return None

        info = stock.info
        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change_pct = ((current_price - prev_close) / prev_close) * 100

        # 기술적 분석
        tech_score, signals = simple_technical_score(df)

        # 테마 분석
        theme_score, matched_theme = get_theme_score(sector, industry)

        total = tech_score + theme_score

        result = {
            'Ticker': ticker,
            'Name': name,
            'Sector': sector,
            'Industry': industry,
            'Price': current_price,
            'Change%': change_pct,
            'Total_Score': total,
            'Tech_Score': tech_score,
            'Theme_Score': theme_score,
            'Signals': signals,
            'Theme': matched_theme
        }

        if show_detail:
            print(f"\n{'='*60}")
            print(f"Stock Analysis: {ticker}")
            print(f"{'='*60}")
            print(f"Name: {name}")
            print(f"Sector: {sector}")
            print(f"Industry: {industry}")
            print(f"Price: ${current_price:.2f} ({change_pct:+.2f}%)")
            print(f"\nScores:")
            print(f"  Technical: {tech_score}/75")
            print(f"  Theme: {theme_score}/25")
            print(f"  TOTAL: {total}/100")
            print(f"\nSignals: {signals}")
            print(f"Theme: {matched_theme}")

            if total >= 80:
                print("\n[BUY] Strong Buy Recommendation!")
            elif total >= 70:
                print("\n[WATCH] Watch List")
            elif total >= 50:
                print("\n[HOLD] Hold/Monitor")
            else:
                print("\n[PASS] Pass")

        return result

    except Exception as e:
        if show_detail:
            print(f"[ERROR] Analysis failed for {ticker}: {e}")
        return None


def analyze_multiple_stocks(tickers, period='6mo', min_score=0):
    """여러 종목 일괄 분석"""
    print(f"\n{'='*60}")
    print(f"Analyzing {len(tickers)} stocks...")
    print(f"{'='*60}\n")

    results = []
    for idx, ticker in enumerate(tickers, 1):
        print(f"[{idx}/{len(tickers)}] {ticker}...", end=' ')
        result = analyze_stock_detailed(ticker, period=period, show_detail=False)
        if result:
            results.append(result)
            print(f"OK (Score: {result['Total_Score']})")
        else:
            print("Failed")

    if not results:
        print("\n[ERROR] No results obtained.")
        return None

    df = pd.DataFrame(results)
    df = df.sort_values('Total_Score', ascending=False)

    # 결과 출력
    print(f"\n{'='*60}")
    print("Analysis Results Summary")
    print(f"{'='*60}\n")

    display_cols = ['Ticker', 'Name', 'Price', 'Change%', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Theme']
    print(df[display_cols].to_string(index=False))

    # 추천 종목
    recommendations = df[df['Total_Score'] >= min_score]

    if not recommendations.empty and min_score > 0:
        print(f"\n{'='*60}")
        print(f"[RECOMMENDATIONS] ({min_score}+ points): {len(recommendations)} stocks")
        print(f"{'='*60}\n")
        rec_cols = ['Ticker', 'Name', 'Total_Score', 'Signals']
        print(recommendations[rec_cols].to_string(index=False))

    return df


def sector_analysis_menu():
    """섹터별 분석 메뉴"""
    print("\n" + "="*60)
    print("Sector Analysis")
    print("="*60)
    print("\n[1] Energy Sector (Trump Policy Beneficiary)")
    print("[2] Defense/Aerospace Sector")
    print("[3] AI/Technology Sector")
    print("[4] Finance Sector")
    print("[5] All Trump Sectors Combined")
    print("[0] Back to Main Menu")

    choice = input("\nSelect sector: ").strip()

    sector_stocks = {
        '1': {
            'name': 'Energy',
            'tickers': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'MPC']
        },
        '2': {
            'name': 'Defense/Aerospace',
            'tickers': ['LMT', 'RTX', 'NOC', 'GD', 'BA', 'LHX', 'HWM', 'TDG']
        },
        '3': {
            'name': 'AI/Technology',
            'tickers': ['NVDA', 'AMD', 'AVGO', 'MSFT', 'GOOGL', 'META', 'AAPL', 'TSLA']
        },
        '4': {
            'name': 'Finance',
            'tickers': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'BLK', 'SCHW']
        },
        '5': {
            'name': 'All Trump Sectors',
            'tickers': ['XOM', 'CVX', 'LMT', 'RTX', 'NVDA', 'AMD', 'JPM', 'BAC', 'NEE', 'DUK']
        }
    }

    if choice in sector_stocks:
        sector_info = sector_stocks[choice]
        print(f"\nAnalyzing {sector_info['name']} Sector...")

        min_score = input("Minimum score for recommendation (default: 70): ").strip()
        min_score = int(min_score) if min_score.isdigit() else 70

        df = analyze_multiple_stocks(sector_info['tickers'], min_score=min_score)

        if df is not None:
            save = input("\nSave results to CSV? (y/n): ").strip().lower()
            if save == 'y':
                filename = f"sector_{sector_info['name'].replace('/', '_')}_analysis.csv"
                df.to_csv(filename, index=False, encoding='utf-8-sig')
                print(f"[SAVED] {filename}")


def custom_ticker_analysis():
    """사용자 지정 종목 분석"""
    print("\n" + "="*60)
    print("Custom Ticker Analysis")
    print("="*60)

    tickers_input = input("\nEnter tickers (comma-separated, e.g., AAPL,MSFT,TSLA): ").strip()

    if not tickers_input:
        print("[ERROR] No tickers entered.")
        return

    tickers = [t.strip().upper() for t in tickers_input.split(',')]

    period = input("Analysis period (3mo/6mo/1y, default: 6mo): ").strip()
    period = period if period in ['3mo', '6mo', '1y', '2y'] else '6mo'

    min_score = input("Minimum score for recommendation (default: 70): ").strip()
    min_score = int(min_score) if min_score.isdigit() else 70

    df = analyze_multiple_stocks(tickers, period=period, min_score=min_score)

    if df is not None:
        save = input("\nSave results to CSV? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"custom_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"[SAVED] {filename}")


def single_stock_detail():
    """개별 종목 상세 분석"""
    print("\n" + "="*60)
    print("Single Stock Detailed Analysis")
    print("="*60)

    ticker = input("\nEnter ticker symbol: ").strip().upper()

    if not ticker:
        print("[ERROR] No ticker entered.")
        return

    period = input("Analysis period (3mo/6mo/1y, default: 6mo): ").strip()
    period = period if period in ['3mo', '6mo', '1y', '2y'] else '6mo'

    result = analyze_stock_detailed(ticker, period=period, show_detail=True)

    if result:
        # 추가 정보 출력
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            print(f"\n{'='*60}")
            print("Additional Information")
            print(f"{'='*60}")
            print(f"Market Cap: ${info.get('marketCap', 0):,}")
            print(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
            print(f"Dividend Yield: {info.get('dividendYield', 0)*100:.2f}%")
            print(f"52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}")
            print(f"52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}")
        except:
            pass


def quick_scan():
    """빠른 스캔 - 주요 종목 30개"""
    print("\n" + "="*60)
    print("Quick Scan - Top 30 Stocks")
    print("="*60)

    # S&P 500 주요 종목 + 트럼프 수혜주
    top_stocks = [
        # 기술
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'AVGO',
        # 에너지
        'XOM', 'CVX', 'COP', 'SLB', 'EOG',
        # 방산
        'LMT', 'RTX', 'NOC', 'GD', 'BA',
        # 금융
        'JPM', 'BAC', 'WFC', 'GS', 'MS',
        # 원전/유틸리티
        'NEE', 'DUK', 'SO', 'D',
        # 기타
        'UNH', 'JNJ', 'V'
    ]

    min_score = input("Minimum score for recommendation (default: 70): ").strip()
    min_score = int(min_score) if min_score.isdigit() else 70

    df = analyze_multiple_stocks(top_stocks, min_score=min_score)

    if df is not None:
        save = input("\nSave results to CSV? (y/n): ").strip().lower()
        if save == 'y':
            filename = f"quick_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"[SAVED] {filename}")


def main_menu():
    """메인 메뉴"""
    while True:
        print("\n" + "="*60)
        print("Quant Trading System - Interactive Menu")
        print("="*60)
        print("\n[1] Quick Scan (Top 30 Stocks)")
        print("[2] Sector Analysis (Energy, Defense, AI, etc.)")
        print("[3] Custom Ticker Analysis")
        print("[4] Single Stock Detailed Analysis")
        print("[5] Demo (Original 5 stocks)")
        print("[0] Exit")

        choice = input("\nSelect option: ").strip()

        if choice == '0':
            print("\n[EXIT] Thank you for using Quant Trading System!")
            break
        elif choice == '1':
            quick_scan()
        elif choice == '2':
            sector_analysis_menu()
        elif choice == '3':
            custom_ticker_analysis()
        elif choice == '4':
            single_stock_detail()
        elif choice == '5':
            # 원본 데모
            demo_tickers = ['AAPL', 'NVDA', 'TSLA', 'XOM', 'LMT']
            analyze_multiple_stocks(demo_tickers, min_score=70)
        else:
            print("\n[ERROR] Invalid option. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Welcome to Quant Trading System")
    print("Stock Recommendation & Scoring System")
    print("="*60)
    print("\n[NOTE] This is a simplified version using yfinance only.")
    print("For full features with pandas-ta, use Python 3.10-3.13.")

    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Program interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
