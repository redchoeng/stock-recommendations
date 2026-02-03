"""
자동화/AI 수혜 점수 분석기 (Automation & AI Beneficiary Analyzer)
- 객관적 기준 기반 점수 산정
- yfinance 데이터 + 산업 분류 기반

20점 만점:
- AI 인프라 수혜: 10점
- 자동화/로봇 수혜: 10점
"""

import yfinance as yf
from typing import Dict


class AutomationAnalyzer:
    """자동화/AI 수혜 분석기 - 객관적 기준 기반"""

    # GICS 산업 코드별 AI 인프라 점수
    # 레퍼런스: MSCI GICS 산업분류 + AI 관련성
    AI_INFRA_BY_INDUSTRY = {
        # 반도체 (Semiconductors) - AI 연산 핵심
        'Semiconductors': 8,
        'Semiconductor Equipment & Materials': 7,
        'Semiconductor Materials & Equipment': 7,

        # 소프트웨어/클라우드 - AI 서비스
        'Systems Software': 6,
        'Application Software': 5,
        'Internet Services & Infrastructure': 7,
        'IT Consulting & Other Services': 4,
        'Data Processing & Outsourced Services': 5,

        # 통신장비 - AI 네트워킹
        'Communications Equipment': 5,
        'Technology Hardware, Storage & Peripherals': 5,

        # 인터넷 서비스
        'Interactive Media & Services': 6,
        'Interactive Home Entertainment': 3,
    }

    # GICS 산업 코드별 자동화/로봇 점수
    # 레퍼런스: 산업 자동화 도입률 + 로봇 밀도
    AUTOMATION_BY_INDUSTRY = {
        # 산업 자동화 장비
        'Industrial Machinery & Supplies & Components': 8,
        'Electrical Components & Equipment': 7,
        'Industrial Machinery': 8,

        # 반도체 장비 - 공정 자동화
        'Semiconductor Equipment & Materials': 8,
        'Semiconductor Materials & Equipment': 8,

        # 전자 장비
        'Electronic Equipment & Instruments': 6,
        'Electronic Manufacturing Services': 5,
        'Technology Distributors': 4,

        # 항공우주/방산 - 고급 자동화
        'Aerospace & Defense': 6,

        # 건설/중장비 - 자율주행 장비
        'Construction Machinery & Heavy Transportation Equipment': 6,
        'Construction & Engineering': 4,

        # 물류 자동화
        'Air Freight & Logistics': 5,
        'Cargo Ground Transportation': 4,
    }

    # 특정 기업 추가 점수 (공시/발표 기반 검증된 데이터)
    # 레퍼런스: 기업 10-K, 실적발표, 공식 발표
    AI_VERIFIED_COMPANIES = {
        # GPU/AI 칩 제조사 (AI 매출 비중 공시 기반)
        'NVDA': {'bonus': 2, 'ref': 'Data Center 매출 $47.5B (FY24), AI GPU 시장점유율 80%+'},
        'AMD': {'bonus': 1, 'ref': 'MI300 AI 가속기 출시, Data Center 매출 급성장'},
        'AVGO': {'bonus': 1, 'ref': 'AI 네트워킹 칩, Custom AI 칩 (Google TPU 등)'},

        # 클라우드 AI (AI 서비스 매출 공시)
        'MSFT': {'bonus': 1, 'ref': 'Azure AI 서비스, Copilot, OpenAI 투자 $13B'},
        'GOOGL': {'bonus': 1, 'ref': 'Google Cloud AI, Gemini, TPU 자체개발'},
        'AMZN': {'bonus': 1, 'ref': 'AWS AI/ML 서비스, Trainium/Inferentia 칩'},

        # AI 메모리 (HBM 매출 공시)
        'MU': {'bonus': 1, 'ref': 'HBM3E 양산, AI 메모리 매출 비중 확대'},
    }

    AUTOMATION_VERIFIED_COMPANIES = {
        # 산업용 로봇/자동화 (로봇 매출 공시)
        'TER': {'bonus': 2, 'ref': 'Universal Robots 인수, 협동로봇 시장 선두'},
        'ROK': {'bonus': 1, 'ref': '산업 자동화 솔루션 매출 $8B+'},
        'EMR': {'bonus': 1, 'ref': '공정 자동화, Aspen Technology 인수'},
        'HON': {'bonus': 1, 'ref': '창고 자동화, Intelligrated 인수'},

        # 반도체 장비 (팹 자동화)
        'AMAT': {'bonus': 1, 'ref': '반도체 제조장비 1위, 자동화 공정'},
        'LRCX': {'bonus': 1, 'ref': '에칭/증착 장비, 자동화 솔루션'},
        'KLAC': {'bonus': 1, 'ref': '반도체 검사장비 자동화'},
        'ASML': {'bonus': 1, 'ref': 'EUV 장비 독점, 고도 자동화'},
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
        except Exception as e:
            print(f"[WARNING] {self.ticker} 정보 로드 실패: {e}")
            self.info = {}

    def calculate_ai_infra_score(self) -> Dict:
        """
        AI 인프라 수혜 점수 (10점 만점)

        기준:
        1. 산업 분류 기반 기본 점수 (0-8점)
        2. 검증된 기업 추가 점수 (0-2점)
        """
        industry = self.info.get('industry', '')
        sector = self.info.get('sector', '')

        # 1. 산업 분류 기반 점수
        base_score = 0
        reason = ''

        if industry in self.AI_INFRA_BY_INDUSTRY:
            base_score = self.AI_INFRA_BY_INDUSTRY[industry]
            reason = f'{industry} 산업'
        elif sector == 'Technology':
            base_score = 3
            reason = '기술 섹터'
        elif sector == 'Communication Services':
            base_score = 2
            reason = '통신서비스 섹터'

        # 2. 검증된 기업 추가 점수
        bonus = 0
        ref = ''
        if self.ticker in self.AI_VERIFIED_COMPANIES:
            data = self.AI_VERIFIED_COMPANIES[self.ticker]
            bonus = data['bonus']
            ref = data['ref']

        total = min(base_score + bonus, 10)

        if ref:
            reason = f'{reason} + {ref}'

        return {
            'score': total,
            'reason': reason if reason else 'AI 인프라 무관',
            'is_beneficiary': total > 0,
            'base_score': base_score,
            'bonus': bonus,
            'reference': ref
        }

    def calculate_automation_score(self) -> Dict:
        """
        자동화/로봇 수혜 점수 (10점 만점)

        기준:
        1. 산업 분류 기반 기본 점수 (0-8점)
        2. 검증된 기업 추가 점수 (0-2점)
        """
        industry = self.info.get('industry', '')
        sector = self.info.get('sector', '')

        # 1. 산업 분류 기반 점수
        base_score = 0
        reason = ''

        if industry in self.AUTOMATION_BY_INDUSTRY:
            base_score = self.AUTOMATION_BY_INDUSTRY[industry]
            reason = f'{industry} 산업'
        elif sector == 'Industrials':
            base_score = 3
            reason = '산업재 섹터'
        elif sector == 'Technology':
            base_score = 2
            reason = '기술 섹터'

        # 2. 검증된 기업 추가 점수
        bonus = 0
        ref = ''
        if self.ticker in self.AUTOMATION_VERIFIED_COMPANIES:
            data = self.AUTOMATION_VERIFIED_COMPANIES[self.ticker]
            bonus = data['bonus']
            ref = data['ref']

        total = min(base_score + bonus, 10)

        if ref:
            reason = f'{reason} + {ref}'

        return {
            'score': total,
            'reason': reason if reason else '자동화 무관',
            'is_beneficiary': total > 0,
            'base_score': base_score,
            'bonus': bonus,
            'reference': ref
        }

    def calculate_total_score(self) -> Dict:
        """
        자동화/AI 수혜 총점 계산 (20점 만점)
        """
        ai_result = self.calculate_ai_infra_score()
        auto_result = self.calculate_automation_score()

        total = ai_result['score'] + auto_result['score']

        # 종합 평가
        if total >= 16:
            verdict = "자동화/AI 핵심 수혜"
        elif total >= 12:
            verdict = "자동화/AI 수혜"
        elif total >= 8:
            verdict = "간접 수혜"
        elif total >= 4:
            verdict = "일부 수혜"
        else:
            verdict = "자동화/AI 무관"

        return {
            'total_score': total,
            'ai_infra_score': ai_result['score'],
            'automation_score': auto_result['score'],
            'ai_reason': ai_result['reason'],
            'automation_reason': auto_result['reason'],
            'verdict': verdict,
            'details': {
                'ai_infra': ai_result,
                'automation': auto_result
            }
        }


# 테스트
if __name__ == "__main__":
    test_tickers = ['NVDA', 'TER', 'AAPL', 'ROK', 'XOM']

    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"{ticker} 자동화/AI 수혜 분석")
        print('='*60)

        analyzer = AutomationAnalyzer(ticker)
        result = analyzer.calculate_total_score()

        print(f"AI 인프라: {result['ai_infra_score']}/10")
        print(f"  - {result['ai_reason']}")
        print(f"자동화/로봇: {result['automation_score']}/10")
        print(f"  - {result['automation_reason']}")
        print(f"\n총점: {result['total_score']}/20")
        print(f"평가: {result['verdict']}")
