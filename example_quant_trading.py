"""
퀀트 트레이딩 시스템 간단한 사용 예제
개별 종목 분석 및 소규모 포트폴리오 분석
"""

from quant_trading import StockScorer, StockRecommender
import pandas as pd


def example_single_stock():
    """
    예제 1: 개별 종목 분석
    """
    print("\n" + "="*60)
    print("예제 1: 개별 종목 분석 (AAPL)")
    print("="*60 + "\n")

    # Apple 주식 분석
    scorer = StockScorer('AAPL', period='6mo')

    # 데이터 다운로드
    if scorer.fetch_data():
        # 점수 계산
        result = scorer.calculate_score()

        if result:
            print(f"티커: {result['Ticker']}")
            print(f"총점: {result['Total_Score']}점")
            print(f"  - 기술적 점수: {result['Tech_Score']}점")
            print(f"  - 테마 점수: {result['Theme_Score']}점")
            print(f"\n시그널: {result['Signal_Type']}")
            print(f"매칭 테마: {result['Matched_Theme']}")
            print(f"긍정 뉴스: {result['Positive_News']}개")

            print(f"\n세부 기술적 점수:")
            print(f"  - 이동평균: {result['MA_Score']}점")
            print(f"  - 일목균형표: {result['Ichimoku_Score']}점")
            print(f"  - 채널: {result['Channel_Score']}점")
            print(f"  - 스토캐스틱: {result['Stoch_Score']}점")
            print(f"  - RSI: {result['RSI_Score']}점")


def example_multiple_stocks():
    """
    예제 2: 여러 종목 일괄 분석
    """
    print("\n" + "="*60)
    print("예제 2: 여러 종목 일괄 분석")
    print("="*60 + "\n")

    # 분석할 종목 리스트
    tickers = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'META', 'AMZN']

    recommender = StockRecommender(min_score=70)

    # 분석 실행
    df = recommender.analyze_stocks(tickers)

    # 결과 출력
    if not df.empty:
        recommender.print_summary(df)

        print("분석 결과:")
        print(df[['Ticker', 'Total_Score', 'Tech_Score', 'Theme_Score', 'Signal_Type']].to_string(index=False))

        # 추천 종목 (70점 이상)
        recommendations = recommender.get_recommendations(df)

        if not recommendations.empty:
            print(f"\n추천 종목 ({recommender.min_score}점 이상):")
            print(recommendations[['Ticker', 'Total_Score', 'Signal_Type']].to_string(index=False))
        else:
            print(f"\n{recommender.min_score}점 이상 종목 없음")


def example_sector_analysis():
    """
    예제 3: 특정 섹터 종목 분석 (에너지/방산)
    """
    print("\n" + "="*60)
    print("예제 3: 트럼프 정책 수혜 섹터 분석")
    print("="*60 + "\n")

    # 에너지, 방산, 원전 관련 종목
    tickers = [
        # 에너지
        'XOM', 'CVX', 'COP', 'SLB',
        # 방산
        'LMT', 'RTX', 'NOC', 'GD', 'BA',
        # 원전/우라늄
        'NEE', 'DUK', 'CEG', 'VST',
        # AI/반도체
        'NVDA', 'AMD', 'AVGO'
    ]

    recommender = StockRecommender(min_score=75)

    # 분석
    df = recommender.analyze_stocks(tickers)

    if not df.empty:
        # 테마별 그룹화
        print("테마별 점수:")
        theme_summary = df.groupby('Matched_Theme').agg({
            'Total_Score': ['count', 'mean', 'max'],
            'Ticker': lambda x: ', '.join(x.head(3))
        })
        print(theme_summary)

        # 고득점 종목
        recommendations = recommender.get_recommendations(df)

        if not recommendations.empty:
            print(f"\n추천 종목 ({recommender.min_score}점 이상):")
            cols = ['Ticker', 'Total_Score', 'Matched_Theme', 'Signal_Type']
            print(recommendations[cols].to_string(index=False))


def main():
    """메인 함수 - 모든 예제 실행"""

    print("\n" + "🚀 "*20)
    print("퀀트 트레이딩 시스템 사용 예제")
    print("🚀 "*20)

    # 예제 1: 개별 종목
    example_single_stock()

    # 예제 2: 여러 종목
    example_multiple_stocks()

    # 예제 3: 섹터 분석
    example_sector_analysis()

    print("\n" + "="*60)
    print("✅ 모든 예제 실행 완료!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
