"""
자동 데모 스크립트 - 모든 기능을 순차적으로 시연
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
    except:
        return None


def demo_section(title, tickers, description):
    """데모 섹션"""
    print(f"\n\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    print(f"{description}\n")

    results = []
    for ticker in tickers:
        print(f"Analyzing {ticker}...", end=' ')
        result = analyze_stock(ticker)
        if result:
            results.append(result)
            print(f"OK (Score: {result['Total_Score']})")
        else:
            print("Failed")
        time.sleep(0.3)

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('Total_Score', ascending=False)

        print(f"\n{'-'*70}")
        print("Results:")
        print(f"{'-'*70}\n")

        display_cols = ['Ticker', 'Name', 'Price', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Theme']
        print(df[display_cols].to_string(index=False))

        # 상위 3개
        top3 = df.head(3)
        print(f"\n{'-'*70}")
        print("TOP 3 STOCKS:")
        print(f"{'-'*70}")
        for idx, row in top3.iterrows():
            print(f"\n#{len(top3) - len(top3[top3['Total_Score'] > row['Total_Score']]):} {row['Ticker']} - {row['Name']}")
            print(f"   Score: {row['Total_Score']} (Tech: {row['Tech_Score']}, Theme: {row['Theme_Score']})")
            print(f"   Signals: {row['Signals']}")
            print(f"   Theme: {row['Theme']}")

        return df
    return None


def main():
    """메인 자동 데모"""
    print("\n" + "="*70)
    print(" "*15 + "QUANT TRADING SYSTEM")
    print(" "*10 + "Automated Demo - All Features")
    print("="*70)

    # Demo 1: 에너지 섹터
    energy_stocks = ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX']
    demo_section(
        "DEMO 1: Energy Sector Analysis",
        energy_stocks,
        "Trump policy beneficiary - Oil & Gas companies"
    )

    input("\n\nPress Enter to continue to next demo...")

    # Demo 2: 방산/항공우주
    defense_stocks = ['LMT', 'RTX', 'NOC', 'GD', 'BA', 'LHX']
    demo_section(
        "DEMO 2: Defense & Aerospace Sector",
        defense_stocks,
        "Defense spending increase - Aerospace & Defense companies"
    )

    input("\n\nPress Enter to continue to next demo...")

    # Demo 3: AI/기술
    tech_stocks = ['NVDA', 'AMD', 'AVGO', 'MSFT', 'GOOGL', 'META']
    demo_section(
        "DEMO 3: AI & Technology Sector",
        tech_stocks,
        "AI boom - Semiconductors & Tech giants"
    )

    input("\n\nPress Enter to continue to next demo...")

    # Demo 4: 종합 분석
    mixed_stocks = ['XOM', 'LMT', 'NVDA', 'JPM', 'AAPL', 'TSLA', 'NEE', 'UNH']
    df_final = demo_section(
        "DEMO 4: Mixed Portfolio Analysis",
        mixed_stocks,
        "Diversified portfolio across sectors"
    )

    # 최종 요약
    if df_final is not None:
        print(f"\n\n{'='*70}")
        print("FINAL SUMMARY")
        print(f"{'='*70}\n")

        print(f"Total Stocks Analyzed: {len(df_final)}")
        print(f"Average Score: {df_final['Total_Score'].mean():.1f}")
        print(f"Highest Score: {df_final['Total_Score'].max()} ({df_final.iloc[0]['Ticker']})")

        print(f"\nScore Distribution:")
        print(f"  80+ points: {len(df_final[df_final['Total_Score'] >= 80])} stocks")
        print(f"  70-79 points: {len(df_final[(df_final['Total_Score'] >= 70) & (df_final['Total_Score'] < 80)])} stocks")
        print(f"  50-69 points: {len(df_final[(df_final['Total_Score'] >= 50) & (df_final['Total_Score'] < 70)])} stocks")
        print(f"  <50 points: {len(df_final[df_final['Total_Score'] < 50])} stocks")

        recommendations = df_final[df_final['Total_Score'] >= 70]

        if not recommendations.empty:
            print(f"\n{'='*70}")
            print(f"BUY RECOMMENDATIONS (70+ points): {len(recommendations)} stocks")
            print(f"{'='*70}\n")
            rec_cols = ['Ticker', 'Name', 'Total_Score', 'Theme', 'Signals']
            print(recommendations[rec_cols].to_string(index=False))

            # CSV 저장
            filename = f"recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            recommendations.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n[SAVED] Results saved to: {filename}")

    print(f"\n\n{'='*70}")
    print("DEMO COMPLETED!")
    print(f"{'='*70}\n")

    print("Next Steps:")
    print("1. Run 'python demo_quant_interactive.py' for interactive menu")
    print("2. Install pandas-ta for full technical analysis features")
    print("3. Use 'python run_stock_recommender.py' for production mode")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Demo interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
