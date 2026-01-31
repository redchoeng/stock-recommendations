"""
매수/매도 가격 추천 데모
검증된 퀀트 전략 + 기술적 분석 기반 가격 제시
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, '.')

from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3
from quant_trading.theme_analyzer import ThemeAnalyzer
from quant_trading.price_recommender import PriceRecommender, print_price_recommendation


def analyze_with_price_recommendation(ticker, strategy='moderate'):
    """
    종목 분석 + 가격 추천

    Args:
        ticker: 종목 티커
        strategy: 'aggressive', 'moderate', 'conservative'

    Returns:
        dict: 분석 결과 + 가격 추천
    """
    try:
        # 데이터 다운로드
        stock = yf.Ticker(ticker)
        df = stock.history(period='2y')

        if df.empty or len(df) < 180:
            print(f"[SKIP] {ticker}: 데이터 부족")
            return None

        # 1. V3 퀀트 분석
        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()

        # 2. 테마 분석
        theme_analyzer = ThemeAnalyzer(ticker)
        theme_result = theme_analyzer.calculate_total_score()

        # 3. 종목 정보
        info = stock.info
        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        current_price = df['Close'].iloc[-1]
        change_pct = ((current_price - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100

        # 4. 총점
        total_score = result_v3['total_score'] + theme_result['total_score']

        # 5. 가격 추천
        price_rec = PriceRecommender(df, current_price)
        price_recommendation = price_rec.get_recommendation(strategy=strategy)

        return {
            'Ticker': ticker,
            'Name': name,
            'Sector': sector,
            'Current_Price': current_price,
            'Change%': change_pct,
            'Total_Score': total_score,
            'V3_Score': result_v3['total_score'],
            'Theme_Score': theme_result['total_score'],
            'V3_Signal': result_v3['signals'],
            'Theme': theme_result['matched_theme'],
            'Price_Recommendation': price_recommendation,
            'result_v3': result_v3,
        }

    except Exception as e:
        print(f"[ERROR] {ticker} 분석 실패: {e}")
        return None


def demo_top_stocks_with_prices():
    """상위 종목 가격 추천"""
    print(f"\n{'='*70}")
    print("DEMO 1: 추천 종목 매수/매도 가격 분석")
    print(f"{'='*70}\n")

    # 분석할 종목
    tickers = [
        'NVDA', 'AMD', 'AVGO',  # 반도체
        'MSFT', 'GOOGL', 'META',  # 빅테크
        'XOM', 'CVX',  # 에너지
        'LMT', 'RTX',  # 방산
        'JPM', 'BAC',  # 금융
    ]

    print(f"분석 종목: {len(tickers)}개\n")

    results = []
    for idx, ticker in enumerate(tickers, 1):
        print(f"[{idx}/{len(tickers)}] {ticker}... ", end='', flush=True)
        result = analyze_with_price_recommendation(ticker, strategy='moderate')
        if result:
            results.append(result)
            print(f"V3: {result['Total_Score']:3.0f}")
        else:
            print("Failed")

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('Total_Score', ascending=False)

        print(f"\n{'='*70}")
        print("종목 순위 (V3 점수 기준)")
        print(f"{'='*70}\n")

        cols = ['Ticker', 'Name', 'Current_Price', 'Total_Score', 'V3_Signal']
        print(df[cols].to_string(index=False))

        # 상위 5개 종목 상세 가격 추천
        print(f"\n\n{'='*70}")
        print("TOP 5 종목 상세 가격 추천")
        print(f"{'='*70}")

        top5 = df.head(5)
        for idx, (_, row) in enumerate(top5.iterrows(), 1):
            print(f"\n\n[{idx}위] {row['Ticker']} - {row['Name']}")
            print(f"섹터: {row['Sector']}")
            print(f"총점: {row['Total_Score']}/100 (V3: {row['V3_Score']}/75, 테마: {row['Theme_Score']}/25)")
            print(f"시그널: {row['V3_Signal'][:60]}...")
            print(f"테마: {row['Theme']}")

            # 가격 추천 출력
            print_price_recommendation(row['Price_Recommendation'], ticker=row['Ticker'])

        # CSV 저장
        # 가격 추천 데이터를 평탄화하여 저장
        export_data = []
        for _, row in df.iterrows():
            pr = row['Price_Recommendation']
            export_data.append({
                'Ticker': row['Ticker'],
                'Name': row['Name'],
                'Total_Score': row['Total_Score'],
                'Current_Price': row['Current_Price'],
                'Entry_Price': pr['entry']['price'],
                'Target_1': pr['exit']['target_1'],
                'Target_2': pr['exit']['target_2'],
                'Target_3': pr['exit']['target_3'],
                'Stop_Loss': pr['stop_loss']['price'],
                'Expected_Profit_2': pr['exit']['expected_profit_2'],
                'Expected_Loss': pr['stop_loss']['expected_loss'],
                'Risk_Reward': pr['risk_reward_ratio'],
                'Support': pr['technical_levels']['support'],
                'Resistance': pr['technical_levels']['resistance'],
            })

        export_df = pd.DataFrame(export_data)
        filename = f"price_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        export_df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n\n[SAVED] 가격 추천 데이터: {filename}")

        return df

    return None


def demo_single_stock_strategies(ticker='NVDA'):
    """개별 종목 전략별 가격 비교"""
    print(f"\n\n{'='*70}")
    print(f"DEMO 2: 전략별 가격 비교 - {ticker}")
    print(f"{'='*70}\n")

    strategies = ['aggressive', 'moderate', 'conservative']

    for strategy in strategies:
        result = analyze_with_price_recommendation(ticker, strategy=strategy)
        if result:
            print(f"\n\n[{strategy.upper()} 전략]")
            print_price_recommendation(result['Price_Recommendation'], ticker=ticker)


def demo_korean_stocks():
    """한국 종목 가격 추천"""
    print(f"\n\n{'='*70}")
    print("DEMO 3: 한국 주요 종목 가격 추천")
    print(f"{'='*70}\n")

    korean_stocks = [
        ('005930.KS', '삼성전자'),
        ('000660.KS', 'SK하이닉스'),
        ('005380.KS', '현대차'),
        ('035420.KS', 'NAVER'),
    ]

    results = []
    for ticker, name_kr in korean_stocks:
        print(f"\n[{name_kr} ({ticker})]")
        result = analyze_with_price_recommendation(ticker, strategy='moderate')
        if result:
            results.append(result)
            print(f"V3 점수: {result['Total_Score']}/100")

            pr = result['Price_Recommendation']
            print(f"\n가격 추천:")
            print(f"  현재가: {result['Current_Price']:,.0f}원")
            print(f"  매수가: {pr['entry']['price']:,.0f}원")
            print(f"  목표가: {pr['exit']['target_1']:,.0f}원 (1차), "
                  f"{pr['exit']['target_2']:,.0f}원 (2차)")
            print(f"  손절가: {pr['stop_loss']['price']:,.0f}원")
            print(f"  기대 수익: +{pr['exit']['expected_profit_2']:.1f}%")
            print(f"  손실 위험: {pr['stop_loss']['expected_loss']:.1f}%")
            print(f"  리스크/리워드: {pr['risk_reward_ratio']:.2f}:1")


def main():
    """메인 함수"""
    print("\n" + "="*70)
    print(" "*12 + "매수/매도 가격 추천 시스템")
    print(" "*10 + "기술적 분석 + 퀀트 전략 기반")
    print("="*70)
    print("\n사용 방법론:")
    print("  - Support/Resistance: Murphy's Technical Analysis")
    print("  - ATR-based Stop Loss: Wilder (1978)")
    print("  - Risk/Reward Ratio: 2:1 기준")
    print("  - Fibonacci Retracement Levels")

    try:
        # Demo 1: 추천 종목 가격 분석
        demo_top_stocks_with_prices()

        # Demo 2: 전략별 가격 비교
        # demo_single_stock_strategies('NVDA')

        # Demo 3: 한국 종목
        # demo_korean_stocks()

        print("\n\n" + "="*70)
        print("모든 데모 완료!")
        print("="*70)
        print("\n참고사항:")
        print("  - 매수/매도 가격은 참고용이며, 최종 판단은 본인 책임")
        print("  - 손절가는 반드시 지켜서 리스크 관리")
        print("  - 분할 매도로 수익 실현 권장")
        print("  - 전략: aggressive(공격적), moderate(중도), conservative(보수적)")

    except KeyboardInterrupt:
        print("\n\n[EXIT] 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
