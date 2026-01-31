"""
모든 데모를 자동으로 실행 - Enter 입력 없이 완전 자동
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import time


def simple_technical_score(df):
    """간단한 기술적 분석"""
    score = 0
    signals = []

    df['SMA_5'] = df['Close'].rolling(window=5).mean()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_60'] = df['Close'].rolling(window=60).mean()

    recent = df.iloc[-1]
    prev = df.iloc[-2]

    if prev['SMA_20'] <= prev['SMA_60'] and recent['SMA_20'] > recent['SMA_60']:
        score += 10
        signals.append("Golden Cross")

    if recent['SMA_5'] > recent['SMA_20'] > recent['SMA_60']:
        score += 5
        signals.append("Alignment")

    try:
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        if not pd.isna(prev.get('RSI')) and not pd.isna(recent.get('RSI')):
            if prev['RSI'] <= 30 and recent['RSI'] > 30:
                score += 10
                signals.append("RSI Oversold Exit")
    except:
        pass

    if df['Close'].iloc[-5:].is_monotonic_increasing:
        score += 5
        signals.append("Uptrend")

    if recent['Volume'] > df['Volume'].iloc[-10:-1].mean() * 1.5:
        score += 5
        signals.append("Volume Surge")

    return score, ' + '.join(signals) if signals else 'No Signal'


def get_theme_score(sector, industry):
    """테마 점수"""
    theme_score = 0
    matched_theme = 'None'

    themes = {
        'Energy': ['Energy', 'Oil', 'Gas'],
        'Defense': ['Defense', 'Aerospace'],
        'AI/Tech': ['Technology', 'Semiconductor', 'Software'],
        'Finance': ['Financial', 'Bank'],
    }

    for theme_name, keywords in themes.items():
        if any(kw in sector for kw in keywords) or any(kw in industry for kw in keywords):
            theme_score = 25
            matched_theme = theme_name
            break

    return theme_score, matched_theme


def analyze_stock(ticker, period='6mo'):
    """종목 분석"""
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

        tech_score, signals = simple_technical_score(df)
        theme_score, matched_theme = get_theme_score(sector, industry)
        total = tech_score + theme_score

        return {
            'Ticker': ticker,
            'Name': name,
            'Sector': sector,
            'Price': current_price,
            'Change%': change_pct,
            'Total_Score': total,
            'Tech_Score': tech_score,
            'Theme_Score': theme_score,
            'Signals': signals,
            'Theme': matched_theme
        }
    except Exception as e:
        print(f"   [Error: {e}]")
        return None


def demo_section(demo_num, title, tickers, description):
    """데모 섹션"""
    print(f"\n\n{'='*70}")
    print(f"DEMO {demo_num}: {title}")
    print(f"{'='*70}")
    print(f"{description}\n")

    results = []
    for ticker in tickers:
        print(f"  [{len(results)+1}/{len(tickers)}] {ticker:6s} ... ", end='', flush=True)
        result = analyze_stock(ticker)
        if result:
            results.append(result)
            print(f"Score: {result['Total_Score']:2d}")
        else:
            print("Failed")
        time.sleep(0.2)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('Total_Score', ascending=False)

        print(f"\n{'-'*70}")
        print(f"Results ({len(df)} stocks):")
        print(f"{'-'*70}\n")

        display_cols = ['Ticker', 'Name', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Theme']
        print(df[display_cols].to_string(index=False))

        # 상위 3개
        top3 = df.head(3)
        print(f"\n{'-'*70}")
        print(f"TOP 3:")
        print(f"{'-'*70}")
        for i, (idx, row) in enumerate(top3.iterrows(), 1):
            print(f"\n  #{i} {row['Ticker']} - {row['Name']}")
            print(f"     Total: {row['Total_Score']} | Tech: {row['Tech_Score']} | Theme: {row['Theme_Score']}")
            print(f"     Signals: {row['Signals']}")

        return df
    return None


def main():
    """메인 함수"""
    print("\n" + "="*70)
    print(" "*20 + "QUANT TRADING SYSTEM")
    print(" "*15 + "Complete Automated Demo")
    print("="*70)
    print("\n[INFO] Analyzing multiple sectors automatically...")
    print("[INFO] This will take approximately 2-3 minutes.\n")

    all_results = []

    # Demo 1: 에너지
    df1 = demo_section(
        1,
        "Energy Sector (Trump Policy)",
        ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX'],
        "Oil & Gas - Trump administration energy policy beneficiaries"
    )
    if df1 is not None:
        all_results.append(df1)

    # Demo 2: 방산
    df2 = demo_section(
        2,
        "Defense & Aerospace",
        ['LMT', 'RTX', 'NOC', 'GD', 'BA', 'LHX'],
        "Defense contractors - Military spending increase"
    )
    if df2 is not None:
        all_results.append(df2)

    # Demo 3: AI/기술
    df3 = demo_section(
        3,
        "AI & Technology",
        ['NVDA', 'AMD', 'AVGO', 'MSFT', 'GOOGL', 'META', 'AAPL'],
        "AI boom - Semiconductors & Tech giants"
    )
    if df3 is not None:
        all_results.append(df3)

    # Demo 4: 금융
    df4 = demo_section(
        4,
        "Financial Services",
        ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C'],
        "Banks - Deregulation expectations"
    )
    if df4 is not None:
        all_results.append(df4)

    # 종합 분석
    if all_results:
        df_all = pd.concat(all_results, ignore_index=True)
        df_all = df_all.sort_values('Total_Score', ascending=False)

        print(f"\n\n{'='*70}")
        print("COMPREHENSIVE ANALYSIS SUMMARY")
        print(f"{'='*70}\n")

        print(f"Total Stocks Analyzed: {len(df_all)}")
        print(f"Average Score: {df_all['Total_Score'].mean():.1f}")
        print(f"Median Score: {df_all['Total_Score'].median():.1f}")
        print(f"Highest Score: {df_all['Total_Score'].max():.0f} ({df_all.iloc[0]['Ticker']} - {df_all.iloc[0]['Name']})")
        print(f"Lowest Score: {df_all['Total_Score'].min():.0f}")

        print(f"\n{'-'*70}")
        print("Score Distribution:")
        print(f"{'-'*70}")
        print(f"  80+ points  : {len(df_all[df_all['Total_Score'] >= 80]):2d} stocks  [STRONG BUY]")
        print(f"  70-79 points: {len(df_all[(df_all['Total_Score'] >= 70) & (df_all['Total_Score'] < 80)]):2d} stocks  [BUY]")
        print(f"  60-69 points: {len(df_all[(df_all['Total_Score'] >= 60) & (df_all['Total_Score'] < 70)]):2d} stocks  [HOLD]")
        print(f"  50-59 points: {len(df_all[(df_all['Total_Score'] >= 50) & (df_all['Total_Score'] < 60)]):2d} stocks  [NEUTRAL]")
        print(f"  <50 points  : {len(df_all[df_all['Total_Score'] < 50]):2d} stocks  [PASS]")

        print(f"\n{'-'*70}")
        print("Theme Distribution:")
        print(f"{'-'*70}")
        theme_counts = df_all['Theme'].value_counts()
        for theme, count in theme_counts.items():
            avg_score = df_all[df_all['Theme'] == theme]['Total_Score'].mean()
            print(f"  {theme:12s}: {count:2d} stocks (Avg Score: {avg_score:.1f})")

        # 추천 종목 (70점 이상)
        recommendations = df_all[df_all['Total_Score'] >= 70]

        print(f"\n\n{'='*70}")
        print(f"BUY RECOMMENDATIONS (70+ points): {len(recommendations)} stocks")
        print(f"{'='*70}\n")

        if not recommendations.empty:
            rec_cols = ['Ticker', 'Name', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Theme', 'Signals']
            print(recommendations[rec_cols].to_string(index=False))

            # CSV 저장
            filename = f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            recommendations.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n[SAVED] Recommendations saved to: {filename}")

            # 전체 결과도 저장
            all_filename = f"all_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_all.to_csv(all_filename, index=False, encoding='utf-8-sig')
            print(f"[SAVED] All results saved to: {all_filename}")
        else:
            print("[INFO] No stocks scored 70+ points.")
            print("[TIP] Current market conditions may not favor technical signals.")

        # TOP 10 종목
        print(f"\n\n{'='*70}")
        print("TOP 10 HIGHEST SCORING STOCKS")
        print(f"{'='*70}\n")

        top10 = df_all.head(10)
        for i, (idx, row) in enumerate(top10.iterrows(), 1):
            print(f"{i:2d}. {row['Ticker']:6s} {row['Name']:30s} Score: {row['Total_Score']:2.0f} | {row['Theme']}")

    print(f"\n\n{'='*70}")
    print("DEMO COMPLETED!")
    print(f"{'='*70}\n")

    print("Available Tools:")
    print("  1. demo_quant_interactive.py  - Interactive menu system")
    print("  2. demo_quant_simple.py       - Simple 5-stock demo")
    print("  3. run_stock_recommender.py   - Full production system")
    print("\nFor full features, install pandas-ta with Python 3.10-3.13")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Demo interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
