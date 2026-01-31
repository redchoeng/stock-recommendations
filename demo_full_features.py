"""
전체 기능 데모 - 모든 기술적 지표 활용
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
                print(f"[SKIP] {ticker}: 데이터 부족")
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
            signal_parts.append(f"테마: {theme_result['matched_theme']}")

        signal_type = ' | '.join(signal_parts) if signal_parts else '시그널 없음'

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
            print(f"종목 분석: {ticker}")
            print(f"{'='*70}")
            print(f"종목명: {name}")
            print(f"섹터: {sector}")
            print(f"산업: {industry}")
            print(f"현재가: ${current_price:.2f} ({change_pct:+.2f}%)")

            print(f"\n점수 (총 100점):")
            print(f"  총점: {total_score}/100")
            print(f"  기술적: {tech_result['total_score']}/75")
            print(f"    - 이동평균: {tech_result['ma_score']}/15")
            print(f"    - 일목균형표: {tech_result['ichimoku_score']}/20")
            print(f"    - 채널: {tech_result['channel_score']}/10")
            print(f"    - 스토캐스틱: {tech_result['stoch_score']}/15")
            print(f"    - RSI: {tech_result['rsi_score']}/15")
            print(f"  테마: {theme_result['total_score']}/25")

            print(f"\n시그널: {signal_type}")
            print(f"테마: {theme_result['matched_theme']}")
            if theme_result['positive_news'] > 0:
                print(f"긍정 뉴스: {theme_result['positive_news']}개")

            if total_score >= 80:
                print("\n[BUY] 강력 매수 추천! ⭐⭐⭐")
            elif total_score >= 70:
                print("\n[WATCH] 관심 종목 ⭐⭐")
            elif total_score >= 60:
                print("\n[HOLD] 보유/모니터링 ⭐")
            else:
                print("\n[PASS] 관망")

        return result

    except Exception as e:
        if show_detail:
            print(f"[ERROR] {ticker} 분석 실패: {e}")
        return None


def demo_single_stock():
    """개별 종목 상세 분석 데모"""
    print("\n" + "="*70)
    print("DEMO 1: 개별 종목 상세 분석 (전체 기능 활용)")
    print("="*70)

    # 에너지 섹터 대표 종목
    ticker = 'XOM'
    print(f"\n[Exxon Mobil (XOM) 전체 분석]\n")

    result = analyze_stock_full(ticker, period='1y', show_detail=True)

    input("\n\nPress Enter to continue...")


def demo_sector_comparison():
    """섹터별 비교 분석 데모"""
    print("\n\n" + "="*70)
    print("DEMO 2: 섹터별 비교 분석 (트럼프 수혜 섹터)")
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
        print("섹터별 분석 결과")
        print(f"{'='*70}\n")

        cols = ['Ticker', 'Name', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Theme']
        print(df[cols].to_string(index=False))

        # 섹터별 평균
        print(f"\n{'='*70}")
        print("섹터별 평균 점수")
        print(f"{'='*70}")

        sector_avg = df.groupby('Theme')['Total_Score'].agg(['count', 'mean', 'max'])
        print(sector_avg)

    input("\n\nPress Enter to continue...")


def demo_recommendations():
    """추천 종목 발굴 데모"""
    print("\n\n" + "="*70)
    print("DEMO 3: 추천 종목 발굴 (70점 이상)")
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

    print(f"\n{len(tickers)}개 종목 분석 중...\n")

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
        print("전체 분석 결과 (점수순)")
        print(f"{'='*70}\n")

        cols = ['Ticker', 'Name', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Signal_Type']
        print(df[cols].head(10).to_string(index=False))

        # 추천 종목 (70점 이상)
        recommendations = df[df['Total_Score'] >= 70]

        print(f"\n\n{'='*70}")
        print(f"매수 추천 종목 (70점 이상): {len(recommendations)}개")
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
            print("현재 시장 상황에서 70점 이상 종목이 없습니다.")
            print("TOP 5 종목:")
            print(df[['Ticker', 'Name', 'Total_Score', 'Signal_Type']].head(5).to_string(index=False))


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
        # Demo 1: 개별 종목 상세
        demo_single_stock()

        # Demo 2: 섹터별 비교
        demo_sector_comparison()

        # Demo 3: 추천 종목 발굴
        demo_recommendations()

        print("\n\n" + "="*70)
        print("모든 데모 완료!")
        print("="*70)
        print("\n사용 가능한 도구:")
        print("  1. demo_full_features.py     - 이 스크립트 (전체 기능)")
        print("  2. demo_quant_interactive.py - 인터랙티브 메뉴")
        print("  3. run_all_demos.py          - 자동 데모")

    except KeyboardInterrupt:
        print("\n\n[EXIT] 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
