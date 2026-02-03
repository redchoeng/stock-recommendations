"""
미국 정부 정책 수혜 분석기 (US Policy Beneficiary Analyzer)
- 실제 법안/정책 기반 객관적 점수 산정
- 공식 발표/공시 데이터 기반 검증

20점 만점 (스케일링 적용):
- CHIPS Act (반도체법): 6점
- IRA (인플레이션 감축법): 6점
- 방산 예산: 4점
- 인프라법 (IIJA): 4점
"""

import yfinance as yf
from typing import Dict


class PolicyAnalyzer:
    """미국 정부 정책 수혜 분석기 - 객관적 기준 기반"""

    # ========== CHIPS and Science Act (2022) ==========
    # 레퍼런스: 미국 상무부 CHIPS Program Office 공식 발표
    # 총 예산: $527억 (제조 $390억, R&D $132억)

    # CHIPS Act 직접 수혜 기업 (상무부 발표 기준)
    CHIPS_ACT_RECIPIENTS = {
        # 상무부 보조금 확정 발표 기업
        'INTC': {'score': 6, 'ref': 'CHIPS 보조금 $85억 확정 (2024.03), 미국 4개 팹 투자'},
        'TSM': {'score': 5, 'ref': 'CHIPS 보조금 $66억 확정, Arizona 팹 3개'},
        'SSNLF': {'score': 5, 'ref': 'CHIPS 보조금 $64억 확정, Texas 팹'},  # 삼성
        'MU': {'score': 4, 'ref': 'CHIPS 보조금 $61억 확정, Idaho/NY 투자'},
        'GFS': {'score': 4, 'ref': 'CHIPS 보조금 $15억 확정'},  # GlobalFoundries
        'TXN': {'score': 3, 'ref': 'CHIPS 보조금 신청, 미국 내 팹 운영'},
    }

    # CHIPS Act 간접 수혜 (장비/소재)
    # 레퍼런스: 미국 내 팹 건설 → 장비 수요 증가
    CHIPS_EQUIPMENT_BY_INDUSTRY = {
        'Semiconductor Equipment & Materials': 5,
        'Semiconductor Materials & Equipment': 5,
        'Semiconductors': 3,  # 팹리스는 간접 수혜
    }

    # ========== Inflation Reduction Act (2022) ==========
    # 레퍼런스: 미국 재무부/IRS 세액공제 가이드라인
    # 총 예산: $3,690억 (에너지/기후)

    # IRA 전기차 세액공제 (30D) - 최대 $7,500/대
    # 조건: 북미 최종조립, 배터리/광물 요건 충족
    IRA_EV_BENEFICIARIES = {
        'TSLA': {'score': 5, 'ref': 'Model 3/Y 세액공제 적격, Fremont/Texas 생산'},
        'GM': {'score': 5, 'ref': 'Bolt/Equinox EV 세액공제 적격, 미국 생산'},
        'F': {'score': 5, 'ref': 'F-150 Lightning/Mustang Mach-E 적격, 미국 생산'},
        'RIVN': {'score': 4, 'ref': 'R1T/R1S 세액공제 적격, Illinois 생산'},
        'LCID': {'score': 4, 'ref': 'Air 세액공제 적격, Arizona 생산'},
    }

    # IRA 재생에너지 세액공제 (ITC/PTC)
    # ITC: 태양광 30%, PTC: 풍력 $27.5/MWh
    IRA_RENEWABLE_BY_INDUSTRY = {
        'Solar': 5,
        'Renewable Electricity': 5,
        'Independent Power Producers & Energy Traders': 4,
        'Electric Utilities': 3,
        'Multi-Utilities': 3,
    }

    IRA_SOLAR_COMPANIES = {
        'FSLR': {'score': 6, 'ref': 'IRA 태양광 제조 세액공제 최대 수혜, 미국 생산'},
        'ENPH': {'score': 4, 'ref': 'IRA 태양광 인버터 세액공제'},
        'NEE': {'score': 4, 'ref': 'IRA 재생에너지 세액공제, 미국 최대 풍력/태양광'},
    }

    # ========== 국방 예산 (NDAA) ==========
    # 레퍼런스: FY2024 NDAA $8,860억, FY2025 요청 $8,950억
    # DoD Top 100 Contractors 기준

    DEFENSE_CONTRACTORS = {
        # DoD 계약 Top 10 (FY2023 기준, usaspending.gov)
        'LMT': {'score': 4, 'ref': 'DoD 계약 1위 $75B+, F-35/미사일'},
        'RTX': {'score': 4, 'ref': 'DoD 계약 2위 $27B+, 미사일/레이더'},
        'GD': {'score': 4, 'ref': 'DoD 계약 3위 $23B+, 함정/전투차량'},
        'BA': {'score': 4, 'ref': 'DoD 계약 4위 $20B+, 군용기/위성'},
        'NOC': {'score': 4, 'ref': 'DoD 계약 5위 $18B+, B-21/잠수함'},
        'LHX': {'score': 3, 'ref': 'DoD 계약 Top 10, 통신/전자전'},
        'HII': {'score': 3, 'ref': '항공모함/잠수함 독점 건조'},
        'LDOS': {'score': 2, 'ref': 'DoD IT 서비스'},
    }

    # 방산 산업 기본 점수
    DEFENSE_BY_INDUSTRY = {
        'Aerospace & Defense': 3,
    }

    # ========== Infrastructure Investment and Jobs Act (IIJA, 2021) ==========
    # 레퍼런스: 총 $1.2조 (신규 $550B)
    # 도로/교량 $110B, 전력망 $65B, 철도 $66B, 광대역 $65B

    INFRASTRUCTURE_BY_INDUSTRY = {
        # 건설/중장비 - 도로/교량 수혜
        'Construction Machinery & Heavy Transportation Equipment': 4,
        'Construction & Engineering': 4,
        'Construction Materials': 4,
        'Heavy Electrical Equipment': 3,

        # 전력망 인프라
        'Electric Utilities': 3,
        'Multi-Utilities': 3,
        'Electrical Components & Equipment': 3,

        # 철도/운송
        'Railroads': 3,
        'Cargo Ground Transportation': 2,

        # 통신 인프라 (광대역)
        'Integrated Telecommunication Services': 2,
    }

    INFRASTRUCTURE_COMPANIES = {
        # 건설장비 대형사
        'CAT': {'score': 4, 'ref': 'IIJA 건설장비 수혜 1위, 미국 점유율 40%+'},
        'DE': {'score': 3, 'ref': 'IIJA 건설/농업 장비'},
        'VMC': {'score': 3, 'ref': 'IIJA 골재 수요 증가, 미국 최대'},
        'MLM': {'score': 3, 'ref': 'IIJA 골재/시멘트 수혜'},
        # 전력망
        'ETN': {'score': 3, 'ref': 'IIJA 전력망 장비 수혜'},
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

    def calculate_chips_score(self) -> Dict:
        """CHIPS Act 수혜 점수 (6점 만점)"""
        industry = self.info.get('industry', '')

        # 1. 직접 수혜 기업 확인
        if self.ticker in self.CHIPS_ACT_RECIPIENTS:
            data = self.CHIPS_ACT_RECIPIENTS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['ref'],
                'is_beneficiary': True
            }

        # 2. 장비/소재 산업 간접 수혜
        if industry in self.CHIPS_EQUIPMENT_BY_INDUSTRY:
            score = self.CHIPS_EQUIPMENT_BY_INDUSTRY[industry]
            return {
                'score': score,
                'reason': f'{industry} - 미국 팹 투자 수혜',
                'is_beneficiary': True
            }

        return {'score': 0, 'reason': 'CHIPS Act 무관', 'is_beneficiary': False}

    def calculate_ira_score(self) -> Dict:
        """IRA 수혜 점수 (6점 만점)"""
        industry = self.info.get('industry', '')

        # 1. 전기차 세액공제 수혜
        if self.ticker in self.IRA_EV_BENEFICIARIES:
            data = self.IRA_EV_BENEFICIARIES[self.ticker]
            return {
                'score': data['score'],
                'reason': data['ref'],
                'is_beneficiary': True
            }

        # 2. 태양광/재생에너지 세액공제
        if self.ticker in self.IRA_SOLAR_COMPANIES:
            data = self.IRA_SOLAR_COMPANIES[self.ticker]
            return {
                'score': data['score'],
                'reason': data['ref'],
                'is_beneficiary': True
            }

        # 3. 산업 기반 수혜
        if industry in self.IRA_RENEWABLE_BY_INDUSTRY:
            score = self.IRA_RENEWABLE_BY_INDUSTRY[industry]
            return {
                'score': score,
                'reason': f'{industry} - IRA 재생에너지 세액공제',
                'is_beneficiary': True
            }

        return {'score': 0, 'reason': 'IRA 무관', 'is_beneficiary': False}

    def calculate_defense_score(self) -> Dict:
        """방산 예산 수혜 점수 (4점 만점)"""
        industry = self.info.get('industry', '')

        # 1. DoD 주요 계약업체
        if self.ticker in self.DEFENSE_CONTRACTORS:
            data = self.DEFENSE_CONTRACTORS[self.ticker]
            return {
                'score': data['score'],
                'reason': data['ref'],
                'is_beneficiary': True
            }

        # 2. 방산 산업 기본
        if industry in self.DEFENSE_BY_INDUSTRY:
            score = self.DEFENSE_BY_INDUSTRY[industry]
            return {
                'score': score,
                'reason': f'{industry} 섹터',
                'is_beneficiary': True
            }

        return {'score': 0, 'reason': '방산 무관', 'is_beneficiary': False}

    def calculate_infrastructure_score(self) -> Dict:
        """인프라법 수혜 점수 (4점 만점)"""
        industry = self.info.get('industry', '')

        # 1. 주요 수혜 기업
        if self.ticker in self.INFRASTRUCTURE_COMPANIES:
            data = self.INFRASTRUCTURE_COMPANIES[self.ticker]
            return {
                'score': data['score'],
                'reason': data['ref'],
                'is_beneficiary': True
            }

        # 2. 산업 기반 수혜
        if industry in self.INFRASTRUCTURE_BY_INDUSTRY:
            score = self.INFRASTRUCTURE_BY_INDUSTRY[industry]
            return {
                'score': score,
                'reason': f'{industry} - IIJA 인프라 투자 수혜',
                'is_beneficiary': True
            }

        return {'score': 0, 'reason': '인프라법 무관', 'is_beneficiary': False}

    def calculate_total_score(self) -> Dict:
        """
        정책 수혜 총점 계산 (20점 만점)
        """
        chips_result = self.calculate_chips_score()
        ira_result = self.calculate_ira_score()
        defense_result = self.calculate_defense_score()
        infra_result = self.calculate_infrastructure_score()

        total = (chips_result['score'] + ira_result['score'] +
                 defense_result['score'] + infra_result['score'])

        # 종합 평가
        if total >= 15:
            verdict = "정책 핵심 수혜"
        elif total >= 10:
            verdict = "정책 수혜"
        elif total >= 5:
            verdict = "간접 수혜"
        else:
            verdict = "정책 수혜 미미"

        # 수혜 정책 목록
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
    test_tickers = ['INTC', 'TSLA', 'LMT', 'CAT', 'FSLR', 'AAPL']

    for ticker in test_tickers:
        print(f"\n{'='*60}")
        print(f"{ticker} 미국 정책 수혜 분석")
        print('='*60)

        analyzer = PolicyAnalyzer(ticker)
        result = analyzer.calculate_total_score()

        print(f"CHIPS Act: {result['chips_score']}/6")
        print(f"  - {result['chips_reason']}")
        print(f"IRA: {result['ira_score']}/6")
        print(f"  - {result['ira_reason']}")
        print(f"방산: {result['defense_score']}/4")
        print(f"  - {result['defense_reason']}")
        print(f"인프라: {result['infra_score']}/4")
        print(f"  - {result['infra_reason']}")
        print(f"\n총점: {result['total_score']}/20")
        print(f"수혜 정책: {result['policy_summary']}")
        print(f"평가: {result['verdict']}")
