"""
티커 점수 조회 도구
사용법: python check_ticker.py AAPL
       python check_ticker.py AAPL MSFT GOOGL
"""

import yfinance as yf
import sys
import io

# Windows 콘솔 UTF-8 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, '.')

from quant_trading.technical_analyzer_v3 import TechnicalAnalyzerV3
from quant_trading.theme_analyzer import ThemeAnalyzer
from quant_trading.price_recommender import PriceRecommender


def check_ticker_score(ticker):
    """티커 점수 분석"""
    try:
        print(f"\n{'='*50}")
        print(f"[{ticker}] 분석 중...")
        print('='*50)

        stock = yf.Ticker(ticker)
        df = stock.history(period='2y')

        if df.empty or len(df) < 180:
            print(f"[오류] 데이터 부족 (최소 180일 필요, 현재: {len(df)}일)")
            return None

        # 기술적 분석 (65점 만점)
        tech_v3 = TechnicalAnalyzerV3(df)
        result_v3 = tech_v3.calculate_total_score()

        # 테마/뉴스 분석 (25점 만점)
        theme_analyzer = ThemeAnalyzer(ticker)
        theme_result = theme_analyzer.calculate_total_score()

        # 총점 (90점 만점)
        total_score = result_v3['total_score'] + theme_result['total_score']

        # 현재가
        info = stock.info
        current_price = info.get('regularMarketPrice') or info.get('previousClose') or df['Close'].iloc[-1]
        company_name = info.get('shortName', ticker)

        # 가격 추천
        recommender = PriceRecommender(df, current_price)
        price_rec = recommender.get_recommendation(strategy='moderate')

        entry_price = price_rec['entry']['price']
        target_1 = price_rec['exit']['target_1']
        target_2 = price_rec['exit']['target_2']
        target_3 = price_rec['exit']['target_3']
        stop_loss = price_rec['stop_loss']['price']

        # 결과 출력
        print(f"\n[종목] {company_name} ({ticker})")
        print(f"[현재가] ${current_price:.2f}")

        print(f"\n{'─'*50}")
        print("[점수 상세]")
        print(f"{'─'*50}")
        print(f"  기술적분석 (65점 만점): {result_v3['total_score']:.1f}점")
        print(f"    - 모멘텀:    {result_v3['momentum_score']:.1f}/25")
        print(f"    - 평균회귀:  {result_v3['mean_reversion_score']:.1f}/20")
        print(f"    - 추세:      {result_v3['trend_score']:.1f}/20")
        print(f"  테마/뉴스 (25점 만점):  {theme_result['total_score']:.1f}점")
        print(f"{'─'*50}")
        print(f"  ** 총점: {total_score:.1f}/90점 **")
        print(f"{'─'*50}")

        # 등급 판정
        if total_score >= 70:
            grade = "[강력추천]"
        elif total_score >= 60:
            grade = "[추천]"
        elif total_score >= 50:
            grade = "[관망]"
        else:
            grade = "[비추천]"

        print(f"  등급: {grade}")

        print(f"\n{'─'*50}")
        print("[매매가격 추천]")
        print(f"{'─'*50}")
        print(f"  매수가:    ${entry_price:.2f}")
        print(f"  1차 익절:  ${target_1:.2f} (+{((target_1/entry_price)-1)*100:.1f}%)")
        print(f"  2차 익절:  ${target_2:.2f} (+{((target_2/entry_price)-1)*100:.1f}%)")
        print(f"  3차 익절:  ${target_3:.2f} (+{((target_3/entry_price)-1)*100:.1f}%)")
        print(f"  손절가:    ${stop_loss:.2f} ({((stop_loss/entry_price)-1)*100:.1f}%)")
        print(f"{'='*50}\n")

        return {
            'ticker': ticker,
            'name': company_name,
            'price': current_price,
            'total_score': total_score,
            'tech_score': result_v3['total_score'],
            'theme_score': theme_result['total_score'],
            'entry': entry_price,
            'target_1': target_1,
            'target_2': target_2,
            'target_3': target_3,
            'stop_loss': stop_loss
        }

    except Exception as e:
        print(f"[오류] 분석 실패: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("사용법: python check_ticker.py [티커]")
        print("예시:   python check_ticker.py AAPL")
        print("        python check_ticker.py AAPL MSFT GOOGL")
        return

    tickers = [t.upper() for t in sys.argv[1:]]

    results = []
    for ticker in tickers:
        result = check_ticker_score(ticker)
        if result:
            results.append(result)

    # 여러 종목인 경우 비교표 출력
    if len(results) > 1:
        print("\n" + "="*60)
        print("[종목 비교]")
        print("="*60)
        print(f"{'티커':<8} {'종목명':<15} {'총점':>8} {'등급':<12}")
        print("-"*60)

        for r in sorted(results, key=lambda x: x['total_score'], reverse=True):
            if r['total_score'] >= 70:
                grade = "[강력추천]"
            elif r['total_score'] >= 60:
                grade = "[추천]"
            elif r['total_score'] >= 50:
                grade = "[관망]"
            else:
                grade = "[비추천]"

            name = r['name'][:12] + "..." if len(r['name']) > 15 else r['name']
            print(f"{r['ticker']:<8} {name:<15} {r['total_score']:>7.1f}점 {grade}")

        print("="*60)


if __name__ == "__main__":
    main()
