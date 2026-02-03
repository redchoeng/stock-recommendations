"""
테마 및 뉴스 분석 클래스 (Theme Analyzer)
트럼프 정책 수혜 섹터 및 뉴스 센티먼트 분석
"""

import yfinance as yf
from bs4 import BeautifulSoup
import requests
from typing import Dict, List
from datetime import datetime, timedelta


class ThemeAnalyzer:
    """
    테마 및 뉴스 분석을 통한 점수 계산 클래스
    총 25점 만점
    """

    # 트럼프 정책 수혜 섹터 키워드 매핑
    TRUMP_THEMES = {
        'Nuclear/Uranium': {
            'keywords': ['Nuclear', 'Uranium', 'Reactor', 'Atomic', 'Enrichment'],
            'sectors': ['Utilities', 'Energy', 'Industrials'],
            'score': 25
        },
        'Oil/Gas': {
            'keywords': ['Oil', 'Gas', 'Petroleum', 'Energy', 'Drilling', 'Refining'],
            'sectors': ['Energy', 'Oil & Gas'],
            'score': 25
        },
        'Defense': {
            'keywords': ['Defense', 'Aerospace', 'Military', 'Weapons', 'Aircraft'],
            'sectors': ['Industrials', 'Aerospace & Defense'],
            'score': 25
        },
        'AI/Data Center': {
            'keywords': ['AI', 'Artificial Intelligence', 'Data Center', 'Cloud', 'GPU', 'Chip', 'Semiconductor'],
            'sectors': ['Technology', 'Information Technology', 'Semiconductors'],
            'score': 25
        },
        'Finance': {
            'keywords': ['Bank', 'Finance', 'Financial', 'Insurance', 'Investment'],
            'sectors': ['Financials', 'Financial Services'],
            'score': 25
        }
    }

    # 긍정적 뉴스 키워드
    POSITIVE_KEYWORDS = [
        'Approval', 'Contract', 'High', 'Growth', 'Increase', 'Up', 'Surge',
        'Record', 'Beat', 'Strong', 'Positive', 'Gain', 'Rally', 'Breakthrough'
    ]

    def __init__(self, ticker: str):
        """
        초기화 함수

        Args:
            ticker: 주식 티커 심볼 (예: 'AAPL')
        """
        self.ticker = ticker
        self.stock = None
        self.sector = None
        self.industry = None
        self.news = []

        # 종목 정보 가져오기
        self._fetch_stock_info()

    def _fetch_stock_info(self):
        """yfinance를 통해 종목 정보 가져오기"""
        try:
            self.stock = yf.Ticker(self.ticker)

            # 섹터 및 산업 정보
            info = self.stock.info
            self.sector = info.get('sector', '')
            self.industry = info.get('industry', '')

            # 최근 뉴스 가져오기 (최근 3일)
            self.news = self.stock.news[:10] if hasattr(self.stock, 'news') else []

        except Exception as e:
            print(f"[WARNING] {self.ticker} 정보 가져오기 실패: {e}")
            self.sector = ''
            self.industry = ''
            self.news = []

    def check_theme_match(self) -> Dict:
        """
        트럼프 정책 수혜 테마 매칭 확인

        Returns:
            dict: {
                'matched': 매칭 여부,
                'theme': 매칭된 테마,
                'score': 점수,
                'reason': 매칭 이유
            }
        """
        result = {
            'matched': False,
            'theme': '',
            'score': 0,
            'reason': ''
        }

        if not self.sector and not self.industry:
            return result

        # 각 테마별로 확인
        for theme_name, theme_data in self.TRUMP_THEMES.items():
            matched = False
            match_reason = []

            # 섹터 매칭 확인
            for sector_keyword in theme_data['sectors']:
                if sector_keyword.lower() in self.sector.lower():
                    matched = True
                    match_reason.append(f"섹터: {self.sector}")
                    break

                if sector_keyword.lower() in self.industry.lower():
                    matched = True
                    match_reason.append(f"산업: {self.industry}")
                    break

            # 산업명에서 키워드 직접 확인
            if not matched:
                for keyword in theme_data['keywords']:
                    if keyword.lower() in self.industry.lower():
                        matched = True
                        match_reason.append(f"키워드: {keyword} in {self.industry}")
                        break

            # 매칭되었으면 결과 반환
            if matched:
                result['matched'] = True
                result['theme'] = theme_name
                result['score'] = theme_data['score']
                result['reason'] = ', '.join(match_reason)
                return result

        return result

    def analyze_news_sentiment(self) -> Dict:
        """
        최근 뉴스 헤드라인 센티먼트 분석

        Returns:
            dict: {
                'positive_count': 긍정 뉴스 수,
                'total_count': 전체 뉴스 수,
                'bonus_score': 가산점,
                'headlines': 긍정 헤드라인 샘플
            }
        """
        result = {
            'positive_count': 0,
            'total_count': len(self.news),
            'bonus_score': 0,
            'headlines': []
        }

        if not self.news:
            return result

        # 최근 3일 이내 뉴스만 필터링
        three_days_ago = datetime.now() - timedelta(days=3)

        for news_item in self.news:
            try:
                # yfinance 새 구조 처리
                if 'content' in news_item:
                    content = news_item['content']
                    title = content.get('title', '')
                    # pubDate 형식: '2026-02-02T23:52:14Z'
                    pub_date_str = content.get('pubDate', '')
                    if pub_date_str:
                        publish_time = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
                    else:
                        continue
                else:
                    title = news_item.get('title', '')
                    publish_time = datetime.fromtimestamp(news_item.get('providerPublishTime', 0))

                if publish_time < three_days_ago:
                    continue

                # 헤드라인에서 긍정 키워드 찾기
                for keyword in self.POSITIVE_KEYWORDS:
                    if keyword.lower() in title.lower():
                        result['positive_count'] += 1
                        result['headlines'].append(title)
                        break

            except Exception as e:
                continue

        # 긍정 뉴스가 많으면 가산점 (최대 5점)
        if result['positive_count'] >= 3:
            result['bonus_score'] = 5
        elif result['positive_count'] >= 2:
            result['bonus_score'] = 3
        elif result['positive_count'] >= 1:
            result['bonus_score'] = 2

        return result

    def calculate_total_score(self) -> Dict:
        """
        전체 테마 분석 점수 계산 (25점 만점)

        Returns:
            dict: {
                'total_score': 총점,
                'theme_score': 테마 점수,
                'news_score': 뉴스 가산점,
                'matched_theme': 매칭된 테마,
                'positive_news': 긍정 뉴스 수
            }
        """
        # 테마 매칭 확인
        theme_result = self.check_theme_match()

        # 뉴스 센티먼트 분석
        news_result = self.analyze_news_sentiment()

        # 총점 계산 (테마 매칭 시 25점, 뉴스 가산점 최대 5점)
        # 하지만 총점은 25점을 넘지 않음
        theme_score = theme_result['score'] if theme_result['matched'] else 0
        total = min(theme_score + news_result['bonus_score'], 25)

        # 최근 뉴스 헤드라인 가져오기 (최대 3개)
        recent_headlines = []
        for news_item in self.news[:5]:
            try:
                # yfinance 새 구조: news[i]['content']['title']
                if 'content' in news_item:
                    title = news_item['content'].get('title', '')
                else:
                    title = news_item.get('title', '')
                if title:
                    recent_headlines.append(title)
            except:
                pass

        result = {
            'total_score': total,
            'theme_score': theme_score,
            'news_score': news_result['bonus_score'],
            'matched_theme': theme_result['theme'] if theme_result['matched'] else '미분류',
            'match_reason': theme_result['reason'] if theme_result['matched'] else '',
            'positive_news': news_result['positive_count'],
            'positive_headlines': recent_headlines[:3]  # 최근 뉴스 3개
        }

        return result

    def get_stock_info_summary(self) -> str:
        """
        종목 정보 요약 반환

        Returns:
            str: 종목 정보 요약 문자열
        """
        if self.stock:
            info = self.stock.info
            name = info.get('longName', self.ticker)
            sector = self.sector or 'N/A'
            industry = self.industry or 'N/A'

            return f"{name} | 섹터: {sector} | 산업: {industry}"
        else:
            return f"{self.ticker} | 정보 없음"
