"""
주식 추천 시스템 (Stock Recommender)
기술적 분석 + 테마 분석을 결합하여 종목 추천
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Dict
import time

from .technical_analyzer_v2 import TechnicalAnalyzerV2
from .theme_analyzer import ThemeAnalyzer


class StockScorer:
    """
    개별 종목에 대한 점수 계산 클래스
    기술적 분석(75점) + 테마 분석(25점) = 총 100점
    """

    def __init__(self, ticker: str, period: str = '6mo'):
        """
        초기화 함수

        Args:
            ticker: 주식 티커 심볼
            period: 데이터 기간 ('6mo', '1y' 등)
        """
        self.ticker = ticker
        self.period = period
        self.df = None
        self.tech_result = None
        self.theme_result = None

    def fetch_data(self) -> bool:
        """
        주가 데이터 다운로드

        Returns:
            bool: 성공 여부
        """
        try:
            stock = yf.Ticker(self.ticker)
            self.df = stock.history(period=self.period)

            if self.df.empty or len(self.df) < 120:
                print(f"[SKIP] {self.ticker}: 데이터 부족 (행 수: {len(self.df)})")
                return False

            return True

        except Exception as e:
            print(f"[ERROR] {self.ticker} 데이터 다운로드 실패: {e}")
            return False

    def calculate_score(self) -> Dict:
        """
        종목 점수 계산 (기술적 분석 + 테마 분석)

        Returns:
            dict: 점수 계산 결과
        """
        if self.df is None or self.df.empty:
            return None

        # 1. 기술적 분석 (75점)
        tech_analyzer = TechnicalAnalyzerV2(self.df)
        self.tech_result = tech_analyzer.calculate_total_score()

        # 2. 테마 분석 (25점)
        theme_analyzer = ThemeAnalyzer(self.ticker)
        self.theme_result = theme_analyzer.calculate_total_score()

        # 3. 총점 계산
        total_score = self.tech_result['total_score'] + self.theme_result['total_score']

        # 4. 시그널 타입 결합
        signal_parts = []

        if self.tech_result['signals'] != '시그널 없음':
            signal_parts.append(self.tech_result['signals'])

        if self.theme_result['matched_theme'] != '미분류':
            signal_parts.append(f"테마: {self.theme_result['matched_theme']}")

        signal_type = ' | '.join(signal_parts) if signal_parts else '시그널 없음'

        result = {
            'Ticker': self.ticker,
            'Total_Score': total_score,
            'Tech_Score': self.tech_result['total_score'],
            'Theme_Score': self.theme_result['total_score'],
            'Signal_Type': signal_type,
            'Matched_Theme': self.theme_result['matched_theme'],
            'Positive_News': self.theme_result['positive_news'],

            # 세부 점수
            'MA_Score': self.tech_result['ma_score'],
            'Ichimoku_Score': self.tech_result['ichimoku_score'],
            'Channel_Score': self.tech_result['channel_score'],
            'Stoch_Score': self.tech_result['stoch_score'],
            'RSI_Score': self.tech_result['rsi_score'],
        }

        return result


class StockRecommender:
    """
    주식 추천 엔진
    S&P500 또는 NASDAQ 종목을 분석하여 80점 이상 종목 추천
    """

    def __init__(self, min_score: int = 80):
        """
        초기화 함수

        Args:
            min_score: 최소 추천 점수 (기본값: 80점)
        """
        self.min_score = min_score
        self.results = []

    def get_sp500_tickers(self) -> List[str]:
        """
        S&P500 종목 리스트 가져오기

        Returns:
            list: S&P500 티커 리스트
        """
        try:
            # Wikipedia에서 S&P500 종목 리스트 크롤링
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_table = tables[0]
            tickers = sp500_table['Symbol'].tolist()

            print(f"[INFO] S&P500 종목 수: {len(tickers)}")
            return tickers

        except Exception as e:
            print(f"[ERROR] S&P500 리스트 가져오기 실패: {e}")
            # 샘플 티커 반환
            return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META']

    def get_nasdaq100_tickers(self) -> List[str]:
        """
        NASDAQ-100 주요 종목 리스트

        Returns:
            list: NASDAQ-100 티커 샘플
        """
        # 주요 NASDAQ-100 종목 샘플
        tickers = [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META',
            'AVGO', 'ASML', 'COST', 'NFLX', 'AMD', 'PEP', 'ADBE', 'CSCO',
            'TMUS', 'INTC', 'CMCSA', 'TXN', 'QCOM', 'AMGN', 'HON', 'INTU',
            'AMAT', 'ISRG', 'BKNG', 'ADP', 'VRTX', 'SBUX'
        ]
        return tickers

    def analyze_stocks(self, tickers: List[str], max_stocks: int = None) -> pd.DataFrame:
        """
        여러 종목을 분석하여 점수 계산

        Args:
            tickers: 분석할 티커 리스트
            max_stocks: 최대 분석 종목 수 (None이면 전체)

        Returns:
            DataFrame: 분석 결과
        """
        self.results = []

        # 분석할 종목 수 제한
        if max_stocks:
            tickers = tickers[:max_stocks]

        total = len(tickers)
        print(f"\n{'='*60}")
        print(f"총 {total}개 종목 분석 시작...")
        print(f"{'='*60}\n")

        for idx, ticker in enumerate(tickers, 1):
            try:
                print(f"[{idx}/{total}] {ticker} 분석 중...", end=' ')

                # StockScorer 생성
                scorer = StockScorer(ticker)

                # 데이터 다운로드
                if not scorer.fetch_data():
                    continue

                # 점수 계산
                result = scorer.calculate_score()

                if result:
                    self.results.append(result)
                    print(f"완료! (점수: {result['Total_Score']}점)")
                else:
                    print("실패")

                # API 호출 제한 방지
                time.sleep(0.5)

            except Exception as e:
                print(f"오류: {e}")
                continue

        # DataFrame으로 변환
        if self.results:
            df = pd.DataFrame(self.results)

            # 점수순 정렬
            df = df.sort_values('Total_Score', ascending=False)

            return df
        else:
            return pd.DataFrame()

    def get_recommendations(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        추천 종목 필터링 (80점 이상)

        Args:
            df: 분석 결과 DataFrame (None이면 self.results 사용)

        Returns:
            DataFrame: 추천 종목 리스트
        """
        if df is None:
            if not self.results:
                return pd.DataFrame()
            df = pd.DataFrame(self.results)

        # 최소 점수 이상 필터링
        recommendations = df[df['Total_Score'] >= self.min_score].copy()

        print(f"\n{'='*60}")
        print(f"📊 추천 종목: {len(recommendations)}개 (최소 {self.min_score}점 이상)")
        print(f"{'='*60}\n")

        return recommendations

    def print_summary(self, df: pd.DataFrame):
        """
        분석 결과 요약 출력

        Args:
            df: 분석 결과 DataFrame
        """
        if df.empty:
            print("[INFO] 분석 결과가 없습니다.")
            return

        print(f"\n{'='*60}")
        print(f"📈 분석 결과 요약")
        print(f"{'='*60}")
        print(f"총 분석 종목 수: {len(df)}")
        print(f"평균 점수: {df['Total_Score'].mean():.1f}점")
        print(f"최고 점수: {df['Total_Score'].max():.0f}점 ({df.iloc[0]['Ticker']})")
        print(f"최저 점수: {df['Total_Score'].min():.0f}점")
        print(f"\n점수 분포:")
        print(f"  90점 이상: {len(df[df['Total_Score'] >= 90])}개")
        print(f"  80-89점: {len(df[(df['Total_Score'] >= 80) & (df['Total_Score'] < 90)])}개")
        print(f"  70-79점: {len(df[(df['Total_Score'] >= 70) & (df['Total_Score'] < 80)])}개")
        print(f"  70점 미만: {len(df[df['Total_Score'] < 70])}개")
        print(f"{'='*60}\n")

    def export_to_csv(self, df: pd.DataFrame, filename: str = 'stock_recommendations.csv'):
        """
        결과를 CSV 파일로 저장

        Args:
            df: 저장할 DataFrame
            filename: 파일명
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n[INFO] 결과 저장 완료: {filename}")
        except Exception as e:
            print(f"\n[ERROR] 파일 저장 실패: {e}")
