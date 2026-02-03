"""
밥값 점수 분석기 (Valuation Analyzer)
- 김기현 파트장 투자 철학 기반
- "밥값 못하면 AI에 대체됩니다"
- 꿈만 있고 숫자 없는 기업 = 도태

35점 만점:
- ROE/ROA (수익성): 15점
- 이익률 (Profit Margin): 10점
- 매출 성장 + 흑자: 10점
"""

import yfinance as yf
from typing import Dict


class ValuationAnalyzer:
    """밥값(가치) 분석기 - 실체 있는 기업인가?"""

    def __init__(self, ticker: str):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
        self.info = {}
        self._fetch_data()

    def _fetch_data(self):
        """재무 데이터 가져오기"""
        try:
            self.info = self.stock.info
        except Exception as e:
            print(f"[WARNING] {self.ticker} 재무 데이터 실패: {e}")
            self.info = {}

    def calculate_roe_score(self) -> Dict:
        """
        ROE/ROA 점수 (15점 만점)
        - ROE 20% 이상: 15점 (밥값 제대로 함)
        - ROE 15-20%: 12점
        - ROE 10-15%: 9점
        - ROE 5-10%: 6점
        - ROE 0-5%: 3점
        - ROE 음수: 0점 (밥값 못함, 도태 대상)
        """
        roe = self.info.get('returnOnEquity', 0) or 0
        roa = self.info.get('returnOnAssets', 0) or 0

        # ROE를 퍼센트로 변환 (yfinance는 소수점으로 제공)
        roe_pct = roe * 100 if abs(roe) < 1 else roe
        roa_pct = roa * 100 if abs(roa) < 1 else roa

        # ROE 기준 점수
        if roe_pct >= 20:
            score = 15
            grade = "밥값 제대로 함"
        elif roe_pct >= 15:
            score = 12
            grade = "우수"
        elif roe_pct >= 10:
            score = 9
            grade = "양호"
        elif roe_pct >= 5:
            score = 6
            grade = "평범"
        elif roe_pct >= 0:
            score = 3
            grade = "미흡"
        else:
            score = 0
            grade = "밥값 못함 - 도태 대상"

        return {
            'score': score,
            'roe': round(roe_pct, 2),
            'roa': round(roa_pct, 2),
            'grade': grade
        }

    def calculate_margin_score(self) -> Dict:
        """
        이익률 점수 (10점 만점)
        - 영업이익률 20% 이상: 10점
        - 영업이익률 15-20%: 8점
        - 영업이익률 10-15%: 6점
        - 영업이익률 5-10%: 4점
        - 영업이익률 0-5%: 2점
        - 영업이익률 음수: 0점 (적자 = 인력 구조조정 대상)
        """
        operating_margin = self.info.get('operatingMargins', 0) or 0
        profit_margin = self.info.get('profitMargins', 0) or 0

        # 퍼센트 변환
        op_margin_pct = operating_margin * 100 if abs(operating_margin) < 1 else operating_margin
        net_margin_pct = profit_margin * 100 if abs(profit_margin) < 1 else profit_margin

        # 영업이익률 기준
        if op_margin_pct >= 20:
            score = 10
            grade = "고마진 비즈니스"
        elif op_margin_pct >= 15:
            score = 8
            grade = "우수 마진"
        elif op_margin_pct >= 10:
            score = 6
            grade = "양호"
        elif op_margin_pct >= 5:
            score = 4
            grade = "박리다매"
        elif op_margin_pct >= 0:
            score = 2
            grade = "마진 압박"
        else:
            score = 0
            grade = "적자 - 구조조정 필요"

        return {
            'score': score,
            'operating_margin': round(op_margin_pct, 2),
            'net_margin': round(net_margin_pct, 2),
            'grade': grade
        }

    def calculate_growth_score(self) -> Dict:
        """
        성장성 점수 (10점 만점)
        - 매출 성장 + 흑자 유지가 핵심
        - 매출만 늘고 적자면 = 꿈만 파는 기업
        """
        revenue_growth = self.info.get('revenueGrowth', 0) or 0
        earnings_growth = self.info.get('earningsGrowth', 0) or 0
        is_profitable = (self.info.get('profitMargins', 0) or 0) > 0

        # 퍼센트 변환
        rev_growth_pct = revenue_growth * 100 if abs(revenue_growth) < 1 else revenue_growth
        earn_growth_pct = earnings_growth * 100 if abs(earnings_growth) < 1 else earnings_growth

        score = 0

        # 흑자 기업인지 먼저 확인
        if not is_profitable:
            # 적자 기업은 최대 3점
            if rev_growth_pct >= 30:
                score = 3
                grade = "적자지만 고성장 - 리스크"
            elif rev_growth_pct >= 10:
                score = 2
                grade = "적자 + 성장 - 위험"
            else:
                score = 0
                grade = "적자 + 저성장 = 도태"
        else:
            # 흑자 기업
            if rev_growth_pct >= 20 and earn_growth_pct >= 10:
                score = 10
                grade = "실적 + 성장 = 완벽"
            elif rev_growth_pct >= 10 and earn_growth_pct >= 0:
                score = 8
                grade = "성장 + 흑자"
            elif rev_growth_pct >= 5:
                score = 6
                grade = "안정 성장"
            elif rev_growth_pct >= 0:
                score = 4
                grade = "안정적"
            else:
                score = 2
                grade = "역성장 - 주의"

        return {
            'score': score,
            'revenue_growth': round(rev_growth_pct, 2),
            'earnings_growth': round(earn_growth_pct, 2),
            'is_profitable': is_profitable,
            'grade': grade
        }

    def calculate_total_score(self) -> Dict:
        """
        밥값 총점 계산 (35점 만점)
        """
        roe_result = self.calculate_roe_score()
        margin_result = self.calculate_margin_score()
        growth_result = self.calculate_growth_score()

        total = roe_result['score'] + margin_result['score'] + growth_result['score']

        # 종합 평가
        if total >= 30:
            verdict = "밥값 제대로 하는 기업"
        elif total >= 25:
            verdict = "괜찮은 기업"
        elif total >= 20:
            verdict = "평범한 기업"
        elif total >= 15:
            verdict = "개선 필요"
        elif total >= 10:
            verdict = "위험 신호"
        else:
            verdict = "AI에 대체될 기업"

        return {
            'total_score': total,
            'roe_score': roe_result['score'],
            'margin_score': margin_result['score'],
            'growth_score': growth_result['score'],
            'roe': roe_result['roe'],
            'operating_margin': margin_result['operating_margin'],
            'revenue_growth': growth_result['revenue_growth'],
            'is_profitable': growth_result['is_profitable'],
            'verdict': verdict,
            'details': {
                'roe': roe_result,
                'margin': margin_result,
                'growth': growth_result
            }
        }


# 테스트
if __name__ == "__main__":
    test_tickers = ['NVDA', 'TER', 'AAPL', 'TSLA']

    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"{ticker} 밥값 분석")
        print('='*50)

        analyzer = ValuationAnalyzer(ticker)
        result = analyzer.calculate_total_score()

        print(f"ROE: {result['roe']}% (점수: {result['roe_score']}/15)")
        print(f"영업이익률: {result['operating_margin']}% (점수: {result['margin_score']}/10)")
        print(f"매출성장: {result['revenue_growth']}% (점수: {result['growth_score']}/10)")
        print(f"흑자 여부: {'O' if result['is_profitable'] else 'X'}")
        print(f"\n총점: {result['total_score']}/35")
        print(f"평가: {result['verdict']}")
