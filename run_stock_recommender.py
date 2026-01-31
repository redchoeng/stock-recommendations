"""
주식 추천 시스템 실행 스크립트
S&P500 또는 NASDAQ 종목 분석 및 추천
"""

import sys
import argparse
from quant_trading import StockRecommender


def main():
    """메인 함수"""

    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(description='주식 추천 시스템')

    parser.add_argument(
        '--market',
        choices=['sp500', 'nasdaq'],
        default='sp500',
        help='분석할 시장 (기본값: sp500)'
    )

    parser.add_argument(
        '--max-stocks',
        type=int,
        default=30,
        help='최대 분석 종목 수 (기본값: 30, 전체 분석: 0)'
    )

    parser.add_argument(
        '--min-score',
        type=int,
        default=80,
        help='최소 추천 점수 (기본값: 80)'
    )

    parser.add_argument(
        '--output',
        default='stock_recommendations.csv',
        help='결과 저장 파일명 (기본값: stock_recommendations.csv)'
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("📊 퀀트 트레이딩 주식 추천 시스템")
    print("="*60)
    print(f"시장: {args.market.upper()}")
    print(f"최대 분석 종목: {args.max_stocks if args.max_stocks > 0 else '전체'}")
    print(f"최소 추천 점수: {args.min_score}점")
    print("="*60 + "\n")

    # 추천 엔진 생성
    recommender = StockRecommender(min_score=args.min_score)

    # 티커 리스트 가져오기
    if args.market == 'sp500':
        tickers = recommender.get_sp500_tickers()
    else:
        tickers = recommender.get_nasdaq100_tickers()

    # 분석 실행
    max_stocks = args.max_stocks if args.max_stocks > 0 else None
    df_results = recommender.analyze_stocks(tickers, max_stocks=max_stocks)

    # 결과 요약 출력
    recommender.print_summary(df_results)

    # 추천 종목 필터링
    df_recommendations = recommender.get_recommendations(df_results)

    # 추천 종목 출력
    if not df_recommendations.empty:
        print("📌 추천 종목 상세:")
        print("-" * 60)

        # 출력할 컬럼 선택
        display_cols = [
            'Ticker', 'Total_Score', 'Tech_Score', 'Theme_Score',
            'Matched_Theme', 'Signal_Type'
        ]

        # pandas 출력 옵션 설정
        import pandas as pd
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 50)

        print(df_recommendations[display_cols].to_string(index=False))
        print("-" * 60)

        # 세부 점수 출력
        print("\n📊 세부 기술적 점수:")
        print("-" * 60)

        detail_cols = [
            'Ticker', 'Total_Score',
            'MA_Score', 'Ichimoku_Score', 'Channel_Score',
            'Stoch_Score', 'RSI_Score', 'Theme_Score'
        ]

        print(df_recommendations[detail_cols].to_string(index=False))
        print("-" * 60)

        # CSV 저장
        recommender.export_to_csv(df_recommendations, args.output)

    else:
        print(f"❌ {args.min_score}점 이상인 추천 종목이 없습니다.")
        print(f"💡 --min-score 값을 낮춰보세요. (예: --min-score 70)")

    # 전체 결과도 저장
    if not df_results.empty:
        all_results_file = args.output.replace('.csv', '_all.csv')
        recommender.export_to_csv(df_results, all_results_file)

    print("\n" + "="*60)
    print("✅ 분석 완료!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
