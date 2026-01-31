"""
검증된 퀀트 전략 (V3) 데모
학술 논문 기반 신호 vs 커스텀 신호 비교
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, '.')

from quant_trading.technical_analyzer_v2 import TechnicalAnalyzerV2
from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3
from quant_trading.theme_analyzer import ThemeAnalyzer


def analyze_stock_comparison(ticker, period='2y'):
    """
    V2(커스텀) vs V3(검증된 퀀트) 비교 분석

    Args:
        ticker: 종목 티커
        period: 분석 기간

    Returns:
        dict: 비교 결과
    """
    try:
        # 데이터 다운로드
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df.empty or len(df) < 180:
            print(f"[SKIP] {ticker}: 데이터 부족 (최소 6개월 필요)")
            return None

        # 1. V2 분석 (커스텀 지표)
        tech_v2 = TechnicalAnalyzerV2(df)
        result_v2 = tech_v2.calculate_total_score()

        # 2. V3 분석 (검증된 퀀트 전략)
        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()

        # 3. 테마 분석
        theme_analyzer = ThemeAnalyzer(ticker)
        theme_result = theme_analyzer.calculate_total_score()

        # 4. 종목 정보
        info = stock.info
        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change_pct = ((current_price - prev_close) / prev_close) * 100

        # 5. 총점 계산
        total_v2 = result_v2['total_score'] + theme_result['total_score']
        total_v3 = result_v3['total_score'] + theme_result['total_score']

        return {
            'Ticker': ticker,
            'Name': name,
            'Sector': sector,
            'Price': current_price,
            'Change%': change_pct,

            # V2 점수
            'V2_Total': total_v2,
            'V2_Tech': result_v2['total_score'],
            'V2_Signal': result_v2['signals'],

            # V3 점수
            'V3_Total': total_v3,
            'V3_Tech': result_v3['total_score'],
            'V3_Momentum': result_v3['momentum_score'],
            'V3_MeanRev': result_v3['mean_reversion_score'],
            'V3_Trend': result_v3['trend_score'],
            'V3_Volatility': result_v3['volatility_score'],
            'V3_Signal': result_v3['signals'],

            # 테마
            'Theme_Score': theme_result['total_score'],
            'Theme': theme_result['matched_theme'],

            # 세부 비교
            'result_v2': result_v2,
            'result_v3': result_v3,
        }

    except Exception as e:
        print(f"[ERROR] {ticker} 분석 실패: {e}")
        return None


def demo_single_comparison(ticker='NVDA'):
    """개별 종목 V2 vs V3 상세 비교"""
    print(f"\n{'='*70}")
    print(f"DEMO 1: 단일 종목 상세 비교 - {ticker}")
    print(f"{'='*70}\n")

    result = analyze_stock_comparison(ticker, period='2y')

    if result:
        print(f"종목: {result['Ticker']} - {result['Name']}")
        print(f"섹터: {result['Sector']}")
        print(f"현재가: ${result['Price']:.2f} ({result['Change%']:+.2f}%)")
        print(f"\n{'='*70}")
        print("V2 (커스텀 지표) vs V3 (검증된 퀀트 전략)")
        print(f"{'='*70}\n")

        # V2 결과
        print("[V2 - 커스텀 지표]")
        print(f"  총점: {result['V2_Total']}/100")
        print(f"  기술적: {result['V2_Tech']}/75")
        print(f"  세부:")
        r2 = result['result_v2']
        print(f"    - 이동평균: {r2['ma_score']}/15")
        print(f"    - 일목균형표: {r2['ichimoku_score']}/20")
        print(f"    - 채널: {r2['channel_score']}/10")
        print(f"    - 스토캐스틱: {r2['stoch_score']}/15")
        print(f"    - RSI: {r2['rsi_score']}/15")
        print(f"  시그널: {result['V2_Signal']}")

        print(f"\n[V3 - 검증된 퀀트 전략]")
        print(f"  총점: {result['V3_Total']}/100")
        print(f"  기술적: {result['V3_Tech']}/75")
        print(f"  세부:")
        print(f"    - Momentum (6M/12M): {result['V3_Momentum']}/30")
        print(f"    - Mean Reversion (RSI/BB): {result['V3_MeanRev']}/20")
        print(f"    - Trend Following (MA): {result['V3_Trend']}/15")
        print(f"    - Volatility Signal: {result['V3_Volatility']}/10")
        print(f"  시그널: {result['V3_Signal']}")

        print(f"\n[테마 분석]")
        print(f"  점수: {result['Theme_Score']}/25")
        print(f"  테마: {result['Theme']}")

        print(f"\n{'='*70}")
        print("차이점 분석:")
        print(f"{'='*70}")
        diff = result['V3_Total'] - result['V2_Total']
        print(f"  총점 차이: {diff:+d} (V3 {'높음' if diff > 0 else '낮음' if diff < 0 else '동일'})")
        print(f"  V2는 단기 기술적 패턴 중심")
        print(f"  V3는 장기 모멘텀 + 통계적 평균회귀 중심")


def demo_multiple_comparison(tickers=None):
    """여러 종목 비교 분석"""
    if tickers is None:
        tickers = ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'TSLA',
                   'XOM', 'CVX', 'LMT', 'RTX', 'JPM']

    print(f"\n\n{'='*70}")
    print(f"DEMO 2: 다중 종목 비교 ({len(tickers)}개 종목)")
    print(f"{'='*70}\n")

    results = []
    for idx, ticker in enumerate(tickers, 1):
        print(f"[{idx}/{len(tickers)}] {ticker}... ", end='', flush=True)
        result = analyze_stock_comparison(ticker)
        if result:
            results.append(result)
            print(f"V2: {result['V2_Total']:3.0f} | V3: {result['V3_Total']:3.0f}")
        else:
            print("Failed")

    if results:
        df = pd.DataFrame(results)

        print(f"\n{'='*70}")
        print("종합 비교 결과")
        print(f"{'='*70}\n")

        # 기본 정보
        cols = ['Ticker', 'Name', 'V2_Total', 'V3_Total', 'Theme']
        print(df[cols].to_string(index=False))

        # 통계
        print(f"\n{'='*70}")
        print("통계 요약")
        print(f"{'='*70}")
        print(f"  평균 점수:")
        print(f"    V2 (커스텀): {df['V2_Total'].mean():.1f}")
        print(f"    V3 (퀀트): {df['V3_Total'].mean():.1f}")
        print(f"\n  V2가 더 높은 종목: {len(df[df['V2_Total'] > df['V3_Total']])}개")
        print(f"  V3가 더 높은 종목: {len(df[df['V3_Total'] > df['V2_Total']])}개")
        print(f"  동일: {len(df[df['V2_Total'] == df['V3_Total']])}개")

        # V3 기준 상위 종목
        df_sorted_v3 = df.sort_values('V3_Total', ascending=False)

        print(f"\n{'='*70}")
        print("V3 (검증된 퀀트) 기준 TOP 5")
        print(f"{'='*70}\n")

        top5 = df_sorted_v3.head(5)
        detail_cols = ['Ticker', 'Name', 'V3_Total', 'V3_Momentum', 'V3_MeanRev', 'V3_Trend', 'V3_Volatility']
        print(top5[detail_cols].to_string(index=False))

        # 추천 종목 (V3 기준 70점 이상)
        recommendations = df_sorted_v3[df_sorted_v3['V3_Total'] >= 70]

        print(f"\n\n{'='*70}")
        print(f"매수 추천 (V3 기준 70점 이상): {len(recommendations)}개")
        print(f"{'='*70}\n")

        if not recommendations.empty:
            rec_cols = ['Ticker', 'Name', 'V3_Total', 'V3_Signal', 'Theme']
            print(recommendations[rec_cols].to_string(index=False))

            # CSV 저장
            filename = f"quant_v3_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            recommendations.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n[SAVED] {filename}")
        else:
            print("현재 70점 이상 종목 없음 (현실적인 시장 상황)")

        return df

    return None


def demo_strategy_explanation():
    """전략 설명"""
    print(f"\n\n{'='*70}")
    print("DEMO 3: 검증된 퀀트 전략 설명")
    print(f"{'='*70}\n")

    print("V3 분석기는 다음 학술 논문 기반 전략을 사용합니다:\n")

    print("1. Momentum Strategy (30점)")
    print("   Reference: Jegadeesh & Titman (1993)")
    print("   - 6개월 모멘텀: 과거 6개월 수익률")
    print("   - 12개월 모멘텀: 과거 2-12개월 수익률 (최근 1개월 제외)")
    print("   - 임계값: 30% (상위 30%), 15% (상위 50%)")
    print("   - 검증: 1965-1989 미국 주식시장, 연 12.01% 초과수익")

    print("\n2. Mean Reversion Strategy (20점)")
    print("   Reference: De Bondt & Thaler (1985)")
    print("   - RSI 과매도 반등: RSI < 30에서 탈출")
    print("   - Bollinger Band 반등: 하단 밴드 터치 후 상승")
    print("   - 검증: 단기 과매도 구간에서 평균 회귀 현상")

    print("\n3. Trend Following (15점)")
    print("   Reference: Hurst, Ooi & Pedersen (2013)")
    print("   - Golden Cross: 20일선 > 60일선 돌파")
    print("   - 정배열: 5 > 20 > 60일선")
    print("   - 검증: 1880년대부터 100년+ 데이터, 모든 자산군에서 효과")

    print("\n4. Low Volatility Anomaly (10점)")
    print("   Reference: Ang et al. (2006)")
    print("   - 저변동성 종목이 고변동성 대비 높은 수익률")
    print("   - 20일 변동성 < 20% (연율): 저변동성 프리미엄")
    print("   - 검증: 1963-2000, 연 1% 초과수익")

    print(f"\n{'='*70}")
    print("V2 (커스텀) vs V3 (검증된 퀀트) 차이점:")
    print(f"{'='*70}")
    print("V2: 단기 기술적 패턴 (일목, 스토캐스틱, RSI 다이버전스)")
    print("    - 장점: 빠른 매매 신호, 단기 트레이딩")
    print("    - 단점: 학술적 검증 부족, 백테스트 없음")
    print("\nV3: 장기 통계 기반 팩터 (모멘텀, 평균회귀, 저변동성)")
    print("    - 장점: 학술 논문으로 검증됨, 수십년 백테스트")
    print("    - 단점: 장기 투자 전략, 단기 수익 제한적")


def main():
    """메인 함수"""
    print("\n" + "="*70)
    print(" "*10 + "QUANT STRATEGY V3 - 검증된 전략 비교")
    print(" "*15 + "Academic Papers Based")
    print("="*70)

    try:
        # Demo 1: 단일 종목 상세 비교
        demo_single_comparison('NVDA')

        # Demo 2: 다중 종목 비교
        demo_multiple_comparison()

        # Demo 3: 전략 설명
        demo_strategy_explanation()

        print("\n\n" + "="*70)
        print("모든 데모 완료!")
        print("="*70)
        print("\n사용 가능한 분석기:")
        print("  1. TechnicalAnalyzerV2 - 커스텀 지표 (단기 트레이딩)")
        print("  2. TechnicalAnalyzerV3 - 검증된 퀀트 전략 (장기 투자)")
        print("\n권장: V3는 학술 논문으로 검증된 전략이므로 신뢰도가 높습니다.")

    except KeyboardInterrupt:
        print("\n\n[EXIT] 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
