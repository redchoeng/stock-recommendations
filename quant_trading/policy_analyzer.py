"""
미국 정부 정책 수혜 분석기 (US Policy Beneficiary Analyzer)
- 트럼프/바이든 정책 기반 수혜주 분석
- 보호무역, 리쇼어링, 에너지 정책 반영

25점 만점:
- CHIPS Act (반도체법): 8점
- IRA (인플레이션 감축법): 7점
- 방산 예산 확대: 5점
- 인프라법 (IIJA): 5점
"""

import yfinance as yf
from typing import Dict


class PolicyAnalyzer:
    """미국 정부 정책 수혜 분석기"""

    # CHIPS Act 수혜 (미국 내 반도체 생산 지원)
    CHIPS_ACT_TICKERS = {
        # 미국 반도체 제조
        'INTC': {'score': 8, 'reason': 'CHIPS Act 최대 수혜 - 미국 팹 투자'},
        'TXN': {'score': 7, 'reason': '미국 내 반도체 생산'},
        'MCHP': {'score': 6, 'reason': '미국 반도체'},
        'ON': {'score': 6, 'reason': '미국 반도체 생산'},
        # 반도체 장비 (미국 팹 건설 수혜)
        'AMAT': {'score': 7, 'reason': '미국 팹 장비 공급'},
        'LRCX': {'score': 7, 'reason': '미국 팹 장비 공급'},
        'KLAC': {'score': 6, 'reason': '미국 팹 검사 장비'},
        # AI 반도체 (미국 생산 확대)
        'NVDA': {'score': 5, 'reason': 'AI 반도체 - 미국 R&D'},
        'AMD': {'score': 5, 'reason': 'AI 반도체 - 미국 설계'},
        'AVGO': {'score': 4, 'reason': '미국 반도체 설계'},
        'QCOM': {'score': 4, 'reason': '미국 반도체 설계'},
        'MU': {'score': 6, 'reason': '미국 메모리 생산'},
        # 테스트/자동화 장비
        'TER': {'score': 7, 'reason': 'CHIPS Act 수혜 - 미국 팹 테스트 장비'},
    }

    # IRA 수혜 (인플레이션 감축법 - 친환경/전기차)
    IRA_TICKERS = {
        # 전기차
        'TSLA': {'score': 7, 'reason': 'IRA 전기차 세액공제 수혜'},
        'F': {'score': 6, 'reason': '미국 전기차 생산'},
        'GM': {'score': 6, 'reason': '미국 전기차 생산'},
        'RIVN': {'score': 5, 'reason': '미국 전기차'},
        # 배터리/소재
        'ALB': {'score': 6, 'reason': '리튬 - IRA 배터리 소재'},
        'FSLR': {'score': 7, 'reason': '태양광 - IRA 최대 수혜'},
        # 친환경 에너지
        'NEE': {'score': 6, 'reason': '재생에너지 - IRA 수혜'},
        'ENPH': {'score': 5, 'reason': '태양광 인버터'},
        # 유틸리티
        'DUK': {'score': 4, 'reason': '전력 인프라'},
        'SO': {'score': 4, 'reason': '전력 인프라'},
        # 전통 에너지 (IRA 일부 수혜)
        'XOM': {'score': 3, 'reason': '탄소포집 세액공제'},
        'CVX': {'score': 3, 'reason': '탄소포집 세액공제'},
    }

    # 방산 예산 확대 (국방 지출 증가)
    DEFENSE_TICKERS = {
        'LMT': {'score': 5, 'reason': '방산 1위 - 국방예산 확대 수혜'},
        'RTX': {'score': 5, 'reason': '방산 대형 - 미사일/레이더'},
        'NOC': {'score': 5, 'reason': '방산 - 스텔스/드론'},
        'GD': {'score': 5, 'reason': '방산 - 탱크/잠수함'},
        'BA': {'score': 4, 'reason': '방산 - 군용기'},
        'LHX': {'score': 4, 'reason': '방산 통신장비'},
        'HII': {'score': 4, 'reason': '방산 - 항공모함/잠수함'},
        # 방산 부품/서비스
        'LDOS': {'score': 3, 'reason': '방산 IT 서비스'},
        'SAIC': {'score': 3, 'reason': '방산 IT'},
    }

    # 인프라법 (IIJA) 수혜
    INFRASTRUCTURE_TICKERS = {
        # 건설/중장비
        'CAT': {'score': 5, 'reason': '인프라법 - 건설장비 1위'},
        'DE': {'score': 4, 'reason': '인프라/농업 장비'},
        'URI': {'score': 4, 'reason': '건설장비 렌탈'},
        'VMC': {'score': 4, 'reason': '골재/시멘트'},
        'MLM': {'score': 4, 'reason': '골재/시멘트'},
        # 전력망/유틸리티
        'NEE': {'score': 4, 'reason': '전력망 인프라'},
        'ETN': {'score': 4, 'reason': '전력 인프라 장비'},
        'EMR': {'score': 3, 'reason': '산업 인프라'},
        # 통신 인프라
        'AMT': {'score': 3, 'reason': '통신 타워'},
        'CCI': {'score': 3, 'reason': '통신 인프라'},
        # 철도
        'UNP': {'score': 3, 'reason': '철도 인프라'},
        'CSX': {'score': 3, 'reason': '철도 인프라'},
        # 산업 자동화 (스마트 인프라)
        'ROK': {'score': 4, 'reason': '스마트 인프라 자동화'},
        'HON': {'score': 3, 'reason': '빌딩/인프라 자동화'},
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

    def calculate_chips_score(self) -> Dict:
        """CHIPS Act 수혜 점수 (8점 만점)"""
        if self.ticker in self.CHIPS_ACT_TICKERS:
            data = self.CHIPS_ACT_TICKERS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['reason'],
                'is_beneficiary': True
            }

        # 섹터로 간접 판단
        industry = self.info.get('industry', '')

        if 'Semiconductor' in industry:
            if 'Equipment' in industry:
                return {'score': 4, 'reason': '반도체 장비 섹터', 'is_beneficiary': True}
            return {'score': 3, 'reason': '반도체 섹터', 'is_beneficiary': True}

        return {'score': 0, 'reason': 'CHIPS Act 무관', 'is_beneficiary': False}

    def calculate_ira_score(self) -> Dict:
        """IRA (인플레이션 감축법) 수혜 점수 (7점 만점)"""
        if self.ticker in self.IRA_TICKERS:
            data = self.IRA_TICKERS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['reason'],
                'is_beneficiary': True
            }

        # 섹터로 간접 판단
        industry = self.info.get('industry', '')
        sector = self.info.get('sector', '')

        if 'Solar' in industry or 'Renewable' in industry:
            return {'score': 4, 'reason': '친환경 에너지', 'is_beneficiary': True}
        elif 'Auto' in industry and 'Electric' in str(self.info.get('longBusinessSummary', '')):
            return {'score': 3, 'reason': '전기차 관련', 'is_beneficiary': True}
        elif sector == 'Utilities':
            return {'score': 2, 'reason': '유틸리티 섹터', 'is_beneficiary': True}

        return {'score': 0, 'reason': 'IRA 무관', 'is_beneficiary': False}

    def calculate_defense_score(self) -> Dict:
        """방산 예산 확대 수혜 점수 (5점 만점)"""
        if self.ticker in self.DEFENSE_TICKERS:
            data = self.DEFENSE_TICKERS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['reason'],
                'is_beneficiary': True
            }

        # 섹터로 간접 판단
        industry = self.info.get('industry', '')

        if 'Aerospace' in industry or 'Defense' in industry:
            return {'score': 3, 'reason': '방산/항공 섹터', 'is_beneficiary': True}

        return {'score': 0, 'reason': '방산 무관', 'is_beneficiary': False}

    def calculate_infrastructure_score(self) -> Dict:
        """인프라법 (IIJA) 수혜 점수 (5점 만점)"""
        if self.ticker in self.INFRASTRUCTURE_TICKERS:
            data = self.INFRASTRUCTURE_TICKERS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['reason'],
                'is_beneficiary': True
            }

        # 섹터로 간접 판단
        industry = self.info.get('industry', '')

        if 'Construction' in industry or 'Building' in industry:
            return {'score': 3, 'reason': '건설 섹터', 'is_beneficiary': True}
        elif 'Industrial' in industry:
            return {'score': 2, 'reason': '산업재 섹터', 'is_beneficiary': True}
        elif 'Railroad' in industry or 'Freight' in industry:
            return {'score': 2, 'reason': '물류/철도', 'is_beneficiary': True}

        return {'score': 0, 'reason': '인프라법 무관', 'is_beneficiary': False}

    def calculate_total_score(self) -> Dict:
        """
        정책 수혜 총점 계산 (25점 만점)
        """
        chips_result = self.calculate_chips_score()
        ira_result = self.calculate_ira_score()
        defense_result = self.calculate_defense_score()
        infra_result = self.calculate_infrastructure_score()

        total = (chips_result['score'] + ira_result['score'] +
                 defense_result['score'] + infra_result['score'])

        # 종합 평가
        if total >= 20:
            verdict = "정책 수혜 핵심주"
        elif total >= 15:
            verdict = "정책 수혜주"
        elif total >= 10:
            verdict = "간접 수혜"
        elif total >= 5:
            verdict = "일부 수혜"
        else:
            verdict = "정책 수혜 미미"

        # 주요 정책 요약
        policies = []
        if chips_result['is_beneficiary']:
            policies.append('CHIPS')
        if ira_result['is_beneficiary']:
            policies.append('IRA')
        if defense_result['is_beneficiary']:
            policies.append('방산')
        if infra_result['is_beneficiary']:
            policies.append('인프라')

        return {
            'total_score': total,
            'chips_score': chips_result['score'],
            'ira_score': ira_result['score'],
            'defense_score': defense_result['score'],
            'infra_score': infra_result['score'],
            'chips_reason': chips_result['reason'],
            'ira_reason': ira_result['reason'],
            'defense_reason': defense_result['reason'],
            'infra_reason': infra_result['reason'],
            'verdict': verdict,
            'policies': policies,
            'policy_summary': ', '.join(policies) if policies else '없음',
            'details': {
                'chips': chips_result,
                'ira': ira_result,
                'defense': defense_result,
                'infrastructure': infra_result
            }
        }


# 테스트
if __name__ == "__main__":
    test_tickers = ['INTC', 'TSLA', 'LMT', 'CAT', 'NVDA', 'AAPL']

    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"{ticker} 미국 정책 수혜 분석")
        print('='*50)

        analyzer = PolicyAnalyzer(ticker)
        result = analyzer.calculate_total_score()

        print(f"CHIPS Act: {result['chips_score']}/8 - {result['chips_reason']}")
        print(f"IRA: {result['ira_score']}/7 - {result['ira_reason']}")
        print(f"방산: {result['defense_score']}/5 - {result['defense_reason']}")
        print(f"인프라: {result['infra_score']}/5 - {result['infra_reason']}")
        print(f"\n총점: {result['total_score']}/25")
        print(f"수혜 정책: {result['policy_summary']}")
        print(f"평가: {result['verdict']}")
