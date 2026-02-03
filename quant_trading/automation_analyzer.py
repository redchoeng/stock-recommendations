"""
자동화/AI 수혜 점수 분석기 (Automation & AI Beneficiary Analyzer)
- 김기현 파트장 투자 철학 기반
- "인건비 30% 폭등 -> 자동화는 필연"
- "걷는 로봇은 시기상조, 바퀴 달린 로봇이 돈 된다"

25점 만점:
- AI 인프라 수혜: 10점
- 자동화/로봇 수혜: 10점
- 리쇼어링(미국 공장 복귀) 수혜: 5점
"""

import yfinance as yf
from typing import Dict, List


class AutomationAnalyzer:
    """자동화/AI 수혜 분석기"""

    # AI 인프라 수혜 기업 (철도 깔리는 중 = 오른다)
    AI_INFRA_TICKERS = {
        # AI 반도체 - 최우선
        'NVDA': {'score': 10, 'reason': 'AI GPU 대장주 - 철도 깔리는 중'},
        'AMD': {'score': 8, 'reason': 'AI GPU 2인자'},
        'AVGO': {'score': 8, 'reason': 'AI 네트워킹/커스텀 칩'},
        'QCOM': {'score': 6, 'reason': 'AI 엣지 칩'},
        'MU': {'score': 7, 'reason': 'HBM 메모리 - AI 필수'},
        'MRVL': {'score': 7, 'reason': 'AI 데이터센터 인프라'},
        # 클라우드/데이터센터
        'MSFT': {'score': 7, 'reason': 'Azure AI + OpenAI'},
        'GOOGL': {'score': 7, 'reason': 'AI 원조 + 클라우드'},
        'AMZN': {'score': 6, 'reason': 'AWS AI 서비스'},
        'META': {'score': 6, 'reason': 'LLaMA AI 개발'},
        # AI 서비스
        'CRM': {'score': 5, 'reason': 'Einstein AI'},
        'PLTR': {'score': 6, 'reason': 'AI 데이터 분석'},
        'SNOW': {'score': 5, 'reason': 'AI 데이터 클라우드'},
    }

    # 자동화/로봇 수혜 기업 (실체 있는 로봇 = 돈 된다)
    AUTOMATION_TICKERS = {
        # 산업용 로봇 - 바퀴 달리거나 팔만 달린 것 = 돈 된다
        'TER': {'score': 10, 'reason': '반도체테스트+협동로봇+물류로봇 = TOP PICK'},
        'ROK': {'score': 8, 'reason': '산업 자동화 선두'},
        'EMR': {'score': 7, 'reason': '공장 자동화'},
        'HON': {'score': 7, 'reason': '물류 자동화'},
        'ABB': {'score': 8, 'reason': '산업용 로봇 대장'},
        # 반도체 장비 (공장 자동화 핵심)
        'AMAT': {'score': 7, 'reason': '반도체 제조 자동화'},
        'LRCX': {'score': 7, 'reason': '반도체 공정 자동화'},
        'KLAC': {'score': 7, 'reason': '반도체 검사 자동화'},
        'ASML': {'score': 8, 'reason': 'EUV 독점 - 자동화 핵심'},
        # 물류 자동화
        'AMZN': {'score': 6, 'reason': '물류 로봇 도입'},
        # 걷는 로봇 = 아직 시기상조
        'TSLA': {'score': 3, 'reason': '옵티머스는 아직 꿈 - 시기상조'},
    }

    # 리쇼어링 수혜 (미국 공장 복귀)
    RESHORING_TICKERS = {
        'TER': {'score': 5, 'reason': '미국 공장에 중국 로봇 못씀 = TER 독식'},
        'NVDA': {'score': 3, 'reason': '미국 AI 팹 수혜'},
        'AMD': {'score': 3, 'reason': '미국 반도체 수혜'},
        'INTC': {'score': 4, 'reason': '미국 반도체 제조'},
        'AMAT': {'score': 4, 'reason': '미국 팹 장비'},
        'LRCX': {'score': 4, 'reason': '미국 팹 장비'},
        'ROK': {'score': 4, 'reason': '미국 공장 자동화'},
        'CAT': {'score': 3, 'reason': '인프라 장비'},
        'DE': {'score': 3, 'reason': '농업 자동화'},
        # 방산 - 미국 생산 필수
        'LMT': {'score': 4, 'reason': '미국 방산 - 국내 생산 필수'},
        'RTX': {'score': 4, 'reason': '미국 방산'},
        'NOC': {'score': 4, 'reason': '미국 방산'},
        'GD': {'score': 4, 'reason': '미국 방산'},
    }

    def __init__(self, ticker: str):
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(ticker)
        self.info = {}
        self._fetch_data()

    def _fetch_data(self):
        """기업 정보 가져오기"""
        try:
            self.info = self.stock.info
        except:
            self.info = {}

    def calculate_ai_infra_score(self) -> Dict:
        """AI 인프라 수혜 점수 (10점 만점)"""
        if self.ticker in self.AI_INFRA_TICKERS:
            data = self.AI_INFRA_TICKERS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['reason'],
                'is_beneficiary': True
            }

        # 섹터로 간접 판단
        sector = self.info.get('sector', '')
        industry = self.info.get('industry', '')

        if 'Semiconductor' in industry:
            return {'score': 4, 'reason': '반도체 섹터', 'is_beneficiary': True}
        elif 'Software' in industry and 'Cloud' in str(self.info.get('longBusinessSummary', '')):
            return {'score': 3, 'reason': '클라우드 관련', 'is_beneficiary': True}
        elif sector == 'Technology':
            return {'score': 2, 'reason': '기술 섹터', 'is_beneficiary': True}

        return {'score': 0, 'reason': 'AI 인프라 무관', 'is_beneficiary': False}

    def calculate_automation_score(self) -> Dict:
        """자동화/로봇 수혜 점수 (10점 만점)"""
        if self.ticker in self.AUTOMATION_TICKERS:
            data = self.AUTOMATION_TICKERS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['reason'],
                'is_beneficiary': True
            }

        # 섹터로 간접 판단
        industry = self.info.get('industry', '')

        if 'Industrial' in industry or 'Machinery' in industry:
            return {'score': 3, 'reason': '산업재 섹터', 'is_beneficiary': True}
        elif 'Semiconductor Equipment' in industry:
            return {'score': 4, 'reason': '반도체 장비', 'is_beneficiary': True}

        return {'score': 0, 'reason': '자동화 무관', 'is_beneficiary': False}

    def calculate_reshoring_score(self) -> Dict:
        """리쇼어링(미국 공장 복귀) 수혜 점수 (5점 만점)"""
        if self.ticker in self.RESHORING_TICKERS:
            data = self.RESHORING_TICKERS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['reason'],
                'is_beneficiary': True
            }

        # 방산/반도체는 기본 수혜
        industry = self.info.get('industry', '')
        if 'Defense' in industry or 'Aerospace' in industry:
            return {'score': 3, 'reason': '방산 - 미국 생산', 'is_beneficiary': True}
        elif 'Semiconductor' in industry:
            return {'score': 2, 'reason': '반도체 리쇼어링', 'is_beneficiary': True}

        return {'score': 0, 'reason': '리쇼어링 무관', 'is_beneficiary': False}

    def calculate_total_score(self) -> Dict:
        """
        자동화/AI 수혜 총점 계산 (25점 만점)
        """
        ai_result = self.calculate_ai_infra_score()
        auto_result = self.calculate_automation_score()
        reshoring_result = self.calculate_reshoring_score()

        total = ai_result['score'] + auto_result['score'] + reshoring_result['score']

        # 종합 평가
        if total >= 20:
            verdict = "자동화 시대 최대 수혜주"
        elif total >= 15:
            verdict = "자동화 트렌드 수혜"
        elif total >= 10:
            verdict = "간접 수혜"
        elif total >= 5:
            verdict = "일부 수혜"
        else:
            verdict = "자동화 무관 - 인건비 리스크"

        return {
            'total_score': total,
            'ai_infra_score': ai_result['score'],
            'automation_score': auto_result['score'],
            'reshoring_score': reshoring_result['score'],
            'ai_reason': ai_result['reason'],
            'automation_reason': auto_result['reason'],
            'reshoring_reason': reshoring_result['reason'],
            'verdict': verdict,
            'details': {
                'ai_infra': ai_result,
                'automation': auto_result,
                'reshoring': reshoring_result
            }
        }


# 테스트
if __name__ == "__main__":
    test_tickers = ['TER', 'NVDA', 'TSLA', 'AAPL', 'LMT']

    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"{ticker} 자동화/AI 수혜 분석")
        print('='*50)

        analyzer = AutomationAnalyzer(ticker)
        result = analyzer.calculate_total_score()

        print(f"AI 인프라: {result['ai_infra_score']}/10 - {result['ai_reason']}")
        print(f"자동화/로봇: {result['automation_score']}/10 - {result['automation_reason']}")
        print(f"리쇼어링: {result['reshoring_score']}/5 - {result['reshoring_reason']}")
        print(f"\n총점: {result['total_score']}/25")
        print(f"평가: {result['verdict']}")
