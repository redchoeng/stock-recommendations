"""
퀀트 트레이딩 주식 추천 시스템
기술적 분석 + 테마 분석을 통한 종목 스코어링 및 추천
"""

# TechnicalAnalyzerV2 (pandas-ta 불필요, 순수 pandas/numpy 구현)
from .technical_analyzer_v2 import TechnicalAnalyzerV2
from .theme_analyzer import ThemeAnalyzer
from .stock_recommender import StockScorer, StockRecommender

# TechnicalAnalyzer (pandas-ta 필요, Python 3.10-3.13 전용)
try:
    from .technical_analyzer import TechnicalAnalyzer
    _has_pandas_ta = True
except ImportError:
    TechnicalAnalyzer = None
    _has_pandas_ta = False

__all__ = [
    'TechnicalAnalyzerV2',
    'ThemeAnalyzer',
    'StockScorer',
    'StockRecommender',
]

if _has_pandas_ta:
    __all__.append('TechnicalAnalyzer')
