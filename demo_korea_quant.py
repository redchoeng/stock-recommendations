"""
한국 증시 퀀트 전략 분석
검증된 학술 전략을 한국 주식에 적용
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import sys
sys.path.insert(0, '.')

from quant_trading.technical_analyzer_v2 import TechnicalAnalyzerV2
from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3


def analyze_korean_stock(ticker, period='2y'):
    """
    한국 종목 분석 (V2 vs V3 비교)

    Args:
        ticker: 종목 코드 (예: '005930.KS', '000660.KS')
        period: 분석 기간

    Returns:
        dict: 분석 결과
    """
    try:
        # yfinance는 .KS (KOSPI), .KQ (KOSDAQ) 접미사 필요
        if not ticker.endswith('.KS') and not ticker.endswith('.KQ'):
            # 기본적으로 KOSPI로 가정
            ticker_symbol = f"{ticker}.KS"
        else:
            ticker_symbol = ticker

        # 데이터 다운로드
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period=period)

        if df.empty or len(df) < 180:
            print(f"[SKIP] {ticker}: 데이터 부족")
            return None

        # 1. V2 분석 (커스텀 지표)
        tech_v2 = TechnicalAnalyzerV2(df)
        result_v2 = tech_v2.calculate_total_score()

        # 2. V3 분석 (검증된 퀀트 전략)
        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()

        # 3. 종목 정보
        info = stock.info
        name = info.get('longName', info.get('shortName', ticker))
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        current_price = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        change_pct = ((current_price - prev_close) / prev_close) * 100

        # 테마 분류 (한국 시장용)
        theme = classify_korean_theme(sector, industry, name)

        return {
            'Ticker': ticker_symbol,
            'Code': ticker.replace('.KS', '').replace('.KQ', ''),
            'Name': name,
            'Sector': sector,
            'Industry': industry,
            'Price': current_price,
            'Change%': change_pct,
            'Theme': theme,

            # V2 점수
            'V2_Total': result_v2['total_score'],
            'V2_Signal': result_v2['signals'],

            # V3 점수
            'V3_Total': result_v3['total_score'],
            'V3_Momentum': result_v3['momentum_score'],
            'V3_MeanRev': result_v3['mean_reversion_score'],
            'V3_Trend': result_v3['trend_score'],
            'V3_Volatility': result_v3['volatility_score'],
            'V3_Signal': result_v3['signals'],

            # 세부 결과
            'result_v2': result_v2,
            'result_v3': result_v3,
        }

    except Exception as e:
        print(f"[ERROR] {ticker} 분석 실패: {e}")
        return None


def classify_korean_theme(sector, industry, name):
    """
    한국 시장 테마 분류

    Args:
        sector: 섹터
        industry: 산업
        name: 종목명

    Returns:
        str: 테마
    """
    name_lower = name.lower() if name else ""
    sector_lower = sector.lower() if sector else ""
    industry_lower = industry.lower() if industry else ""

    # 반도체/IT
    if any(keyword in name_lower or keyword in industry_lower
           for keyword in ['semiconductor', 'hynix', '삼성전자', 'sk하이닉스', 'memory']):
        return '반도체'

    if any(keyword in name_lower or keyword in sector_lower
           for keyword in ['naver', 'kakao', 'internet', 'software', 'platform']):
        return 'IT/플랫폼'

    # 배터리/2차전지
    if any(keyword in name_lower or keyword in industry_lower
           for keyword in ['battery', 'lg에너지', 'samsung sdi', '2차전지', 'lgchem']):
        return '배터리/2차전지'

    # 자동차
    if any(keyword in name_lower or keyword in industry_lower
           for keyword in ['hyundai', 'kia', 'auto', '현대차', '기아']):
        return '자동차'

    # 바이오/제약
    if any(keyword in name_lower or keyword in sector_lower
           for keyword in ['bio', 'pharm', 'healthcare', '제약', '셀트리온']):
        return '바이오/제약'

    # 금융
    if any(keyword in sector_lower or keyword in industry_lower
           for keyword in ['financial', 'bank', 'insurance', '금융', '은행']):
        return '금융'

    # 화학
    if any(keyword in sector_lower or keyword in industry_lower
           for keyword in ['chemical', 'petro', '화학']):
        return '화학'

    # 건설/부동산
    if any(keyword in sector_lower or keyword in industry_lower
           for keyword in ['construction', 'real estate', '건설', '부동산']):
        return '건설'

    # 조선
    if any(keyword in name_lower or keyword in industry_lower
           for keyword in ['shipbuilding', '조선', 'heavy industries']):
        return '조선'

    return '기타'


def demo_korean_major_stocks():
    """한국 주요 종목 분석"""
    print(f"\n{'='*70}")
    print("DEMO 1: 한국 주요 종목 분석 (검증된 퀀트 전략)")
    print(f"{'='*70}\n")

    # 한국 대표 종목 (KOSPI 시가총액 상위)
    korean_stocks = {
        '005930.KS': '삼성전자',
        '000660.KS': 'SK하이닉스',
        '035420.KS': 'NAVER',
        '035720.KS': '카카오',
        '005380.KS': '현대차',
        '051910.KS': 'LG화학',
        '006400.KS': '삼성SDI',
        '068270.KS': '셀트리온',
        '105560.KS': 'KB금융',
        '055550.KS': '신한지주',
        '012330.KS': '현대모비스',
        '000270.KS': '기아',
        '028260.KS': '삼성물산',
        '051900.KS': 'LG생활건강',
        '096770.KS': 'SK이노베이션',
    }

    print(f"분석 종목: {len(korean_stocks)}개\n")

    results = []
    for idx, (ticker, name_kr) in enumerate(korean_stocks.items(), 1):
        print(f"[{idx}/{len(korean_stocks)}] {ticker} ({name_kr})... ", end='', flush=True)
        result = analyze_korean_stock(ticker)
        if result:
            results.append(result)
            print(f"V2: {result['V2_Total']:3.0f} | V3: {result['V3_Total']:3.0f}")
        else:
            print("Failed")

    if results:
        df = pd.DataFrame(results)

        print(f"\n{'='*70}")
        print("분석 결과")
        print(f"{'='*70}\n")

        cols = ['Code', 'Name', 'Price', 'V2_Total', 'V3_Total', 'Theme']
        print(df[cols].to_string(index=False))

        # 통계
        print(f"\n{'='*70}")
        print("통계 요약")
        print(f"{'='*70}")
        print(f"  평균 점수:")
        print(f"    V2 (커스텀): {df['V2_Total'].mean():.1f}")
        print(f"    V3 (검증된 퀀트): {df['V3_Total'].mean():.1f}")
        print(f"\n  V3가 V2보다 높은 종목: {len(df[df['V3_Total'] > df['V2_Total']])}개")
        print(f"  V2가 V3보다 높은 종목: {len(df[df['V2_Total'] > df['V3_Total']])}개")

        # V3 기준 상위 종목
        df_sorted = df.sort_values('V3_Total', ascending=False)

        print(f"\n{'='*70}")
        print("V3 (검증된 퀀트) 기준 TOP 5")
        print(f"{'='*70}\n")

        top5 = df_sorted.head(5)
        detail_cols = ['Code', 'Name', 'V3_Total', 'V3_Momentum', 'V3_MeanRev', 'V3_Trend', 'V3_Volatility']
        print(top5[detail_cols].to_string(index=False))

        # 모멘텀 상위 종목
        print(f"\n{'='*70}")
        print("모멘텀 점수 TOP 5 (6개월/12개월 수익률)")
        print(f"{'='*70}\n")

        df_momentum = df.sort_values('V3_Momentum', ascending=False)
        momentum_cols = ['Code', 'Name', 'V3_Momentum', 'V3_Total', 'V3_Signal']
        print(df_momentum[momentum_cols].head(5).to_string(index=False))

        # 추천 종목 (V3 기준 60점 이상 - 한국 시장은 임계값 낮춤)
        recommendations = df_sorted[df_sorted['V3_Total'] >= 60]

        print(f"\n\n{'='*70}")
        print(f"매수 추천 (V3 기준 60점 이상): {len(recommendations)}개")
        print(f"{'='*70}\n")

        if not recommendations.empty:
            rec_cols = ['Code', 'Name', 'V3_Total', 'V3_Signal', 'Theme']
            print(recommendations[rec_cols].to_string(index=False))

            # CSV 저장
            filename = f"korea_quant_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            recommendations.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n[SAVED] {filename}")
        else:
            print("60점 이상 종목 없음")
            print("\nTOP 3 종목:")
            print(df_sorted[['Code', 'Name', 'V3_Total', 'V3_Signal']].head(3).to_string(index=False))

        return df

    return None


def demo_sector_analysis():
    """섹터별 분석"""
    print(f"\n\n{'='*70}")
    print("DEMO 2: 한국 섹터별 분석")
    print(f"{'='*70}\n")

    sectors = {
        '반도체/IT': [
            '005930.KS',  # 삼성전자
            '000660.KS',  # SK하이닉스
            '035420.KS',  # NAVER
            '035720.KS',  # 카카오
        ],
        '배터리/2차전지': [
            '051910.KS',  # LG화학
            '006400.KS',  # 삼성SDI
            '373220.KS',  # LG에너지솔루션
        ],
        '자동차': [
            '005380.KS',  # 현대차
            '000270.KS',  # 기아
            '012330.KS',  # 현대모비스
        ],
        '바이오/제약': [
            '068270.KS',  # 셀트리온
            '207940.KS',  # 삼성바이오로직스
            '326030.KS',  # SK바이오팜
        ],
    }

    all_results = []

    for sector_name, tickers in sectors.items():
        print(f"\n[{sector_name} 섹터]")
        for ticker in tickers:
            print(f"  {ticker}... ", end='', flush=True)
            result = analyze_korean_stock(ticker)
            if result:
                all_results.append(result)
                print(f"V3: {result['V3_Total']:3.0f} ({result['V3_Signal'][:30]}...)")
            else:
                print("Failed")

    if all_results:
        df = pd.DataFrame(all_results)

        print(f"\n{'='*70}")
        print("섹터별 평균 점수 (V3 기준)")
        print(f"{'='*70}\n")

        sector_stats = df.groupby('Theme').agg({
            'V3_Total': ['count', 'mean', 'max'],
            'V3_Momentum': 'mean'
        }).round(1)
        print(sector_stats)


def demo_single_detail(ticker='005930.KS'):
    """개별 종목 상세 분석"""
    print(f"\n\n{'='*70}")
    print(f"DEMO 3: 개별 종목 상세 분석 - {ticker}")
    print(f"{'='*70}\n")

    result = analyze_korean_stock(ticker)

    if result:
        print(f"종목코드: {result['Code']}")
        print(f"종목명: {result['Name']}")
        print(f"섹터: {result['Sector']}")
        print(f"테마: {result['Theme']}")
        print(f"현재가: {result['Price']:,.0f}원 ({result['Change%']:+.2f}%)")

        print(f"\n{'='*70}")
        print("V2 (커스텀 지표) vs V3 (검증된 퀀트 전략)")
        print(f"{'='*70}\n")

        # V2 결과
        print("[V2 - 커스텀 지표]")
        print(f"  총점: {result['V2_Total']}/75")
        r2 = result['result_v2']
        print(f"  세부:")
        print(f"    - 이동평균: {r2['ma_score']}/15")
        print(f"    - 일목균형표: {r2['ichimoku_score']}/20")
        print(f"    - 채널: {r2['channel_score']}/10")
        print(f"    - 스토캐스틱: {r2['stoch_score']}/15")
        print(f"    - RSI: {r2['rsi_score']}/15")
        print(f"  시그널: {result['V2_Signal']}")

        print(f"\n[V3 - 검증된 퀀트 전략]")
        print(f"  총점: {result['V3_Total']}/75")
        print(f"  세부:")
        print(f"    - Momentum (6M/12M): {result['V3_Momentum']}/30")
        print(f"    - Mean Reversion (RSI/BB): {result['V3_MeanRev']}/20")
        print(f"    - Trend Following (MA): {result['V3_Trend']}/15")
        print(f"    - Volatility Signal: {result['V3_Volatility']}/10")
        print(f"  시그널: {result['V3_Signal']}")

        print(f"\n{'='*70}")
        print("투자 의견:")
        print(f"{'='*70}")
        v3_score = result['V3_Total']
        if v3_score >= 60:
            print("  [BUY] 매수 추천 (검증된 퀀트 전략 기준)")
        elif v3_score >= 50:
            print("  [WATCH] 관심 종목")
        elif v3_score >= 40:
            print("  [HOLD] 보유 관찰")
        else:
            print("  [PASS] 관망")


def main():
    """메인 함수"""
    print("\n" + "="*70)
    print(" "*15 + "한국 증시 퀀트 전략 분석")
    print(" "*10 + "검증된 학술 전략 기반 종목 평가")
    print("="*70)
    print("\n사용 전략:")
    print("  - Momentum: Jegadeesh & Titman (1993)")
    print("  - Mean Reversion: De Bondt & Thaler (1985)")
    print("  - Trend Following: Hurst et al. (2013)")
    print("  - Low Volatility: Ang et al. (2006)")

    try:
        # Demo 1: 주요 종목 분석
        demo_korean_major_stocks()

        # Demo 2: 섹터별 분석
        demo_sector_analysis()

        # Demo 3: 개별 종목 상세
        demo_single_detail('005930.KS')  # 삼성전자

        print("\n\n" + "="*70)
        print("모든 데모 완료!")
        print("="*70)
        print("\n참고사항:")
        print("  - 한국 시장은 미국 대비 변동성이 크므로 점수 해석에 주의")
        print("  - 추천 임계값: 60점 이상 (미국은 70점)")
        print("  - V3 전략은 장기 투자에 적합 (6개월~1년)")

    except KeyboardInterrupt:
        print("\n\n[EXIT] 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
