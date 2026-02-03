"""
가치주/배당주 종목 목록 (기술주 제외)
- 금융, 헬스케어, 필수소비재, 산업재, 에너지, 유틸리티, 소재, 리츠
"""

VALUE_TICKERS = [
    # === Financials (금융) ===
    # 은행
    'JPM', 'BAC', 'WFC', 'C', 'USB', 'PNC', 'TFC', 'COF', 'MTB', 'FITB',
    'HBAN', 'RF', 'CFG', 'KEY', 'ZION',
    # 투자은행/자산운용
    'GS', 'MS', 'BLK', 'SCHW', 'BK', 'STT', 'NTRS', 'AMP', 'RJF',
    # 보험
    'BRK-B', 'PGR', 'CB', 'MMC', 'AON', 'TRV', 'AIG', 'MET', 'AFL', 'PRU',
    'ALL', 'AJG', 'CINF', 'WRB', 'GL', 'AIZ', 'BRO', 'L',
    # 결제/핀테크 (비기술)
    'V', 'MA', 'AXP',
    # 거래소/데이터
    'SPGI', 'ICE', 'CME', 'MCO', 'MSCI', 'NDAQ', 'CBOE', 'FDS',

    # === Healthcare (헬스케어) ===
    # 제약 (빅파마)
    'LLY', 'JNJ', 'MRK', 'ABBV', 'PFE', 'BMY', 'AMGN', 'GILD',
    # 보험/PBM
    'UNH', 'ELV', 'CI', 'CVS', 'HUM', 'CNC', 'MOH',
    # 의료기기
    'ABT', 'MDT', 'SYK', 'BSX', 'BDX', 'EW', 'ZBH', 'BAX', 'HOLX',
    # 진단/생명과학
    'TMO', 'DHR', 'A', 'IQV', 'DGX', 'LH', 'MTD',
    # 병원/서비스
    'HCA', 'MCK', 'CAH',

    # === Consumer Staples (필수소비재) ===
    # 음료
    'KO', 'PEP', 'MNST', 'KDP',
    # 식품
    'MDLZ', 'GIS', 'K', 'HSY', 'KHC', 'CPB', 'SJM', 'HRL', 'TSN', 'CAG',
    # 담배
    'PM', 'MO', 'BTI',
    # 생활용품
    'PG', 'CL', 'KMB', 'CLX', 'CHD',
    # 소매 (필수소비재)
    'WMT', 'COST', 'TGT', 'DG', 'DLTR',

    # === Industrials (산업재) ===
    # 항공우주/방산
    'LMT', 'RTX', 'NOC', 'GD', 'BA', 'LHX', 'HII', 'TDG',
    # 중장비/건설
    'CAT', 'DE', 'CMI', 'PCAR', 'EMR', 'ROK', 'ETN', 'PH', 'ITW',
    'DOV', 'IR', 'AME', 'SWK', 'SNA', 'GNRC',
    # 철도/물류
    'UNP', 'CSX', 'NSC', 'UPS', 'FDX', 'ODFL', 'JBHT', 'CHRW', 'EXPD',
    # 항공
    'DAL', 'UAL', 'LUV', 'AAL',
    # 산업서비스
    'WM', 'RSG', 'GE', 'HON', 'MMM', 'JCI', 'CARR', 'OTIS', 'TT',
    # 인력/컨설팅
    'ADP', 'PAYX', 'CTAS', 'FAST', 'GWW', 'VRSK',

    # === Energy (에너지) ===
    # 통합석유
    'XOM', 'CVX', 'COP', 'OXY', 'EOG', 'DVN', 'FANG', 'APA',
    # 정유
    'MPC', 'PSX', 'VLO',
    # 서비스/장비
    'SLB', 'BKR', 'HAL',
    # 미드스트림
    'WMB', 'KMI', 'OKE', 'TRGP',

    # === Materials (소재) ===
    # 화학
    'LIN', 'APD', 'ECL', 'DD', 'DOW', 'LYB', 'PPG', 'SHW', 'EMN', 'CE',
    # 광업/금속
    'FCX', 'NUE', 'NEM',
    # 건설자재
    'VMC', 'MLM',
    # 농업
    'CTVA', 'CF', 'MOS', 'FMC',
    # 포장재
    'BALL', 'AVY', 'PKG', 'IP', 'SEE', 'AMCR',

    # === Utilities (유틸리티) ===
    # 전력
    'NEE', 'SO', 'DUK', 'AEP', 'D', 'EXC', 'XEL', 'WEC', 'ES', 'ED',
    'DTE', 'ETR', 'PPL', 'AEE', 'FE', 'CMS', 'LNT', 'EVRG', 'PNW', 'NI',
    # 가스
    'SRE', 'PCG', 'ATO', 'NRG', 'CEG',
    # 수도
    'AWK', 'CNP',
    # 재생에너지
    'AES',

    # === Real Estate (리츠) ===
    # 물류/산업용
    'PLD', 'PSA', 'EXR',
    # 통신타워
    'AMT', 'CCI', 'SBAC',
    # 데이터센터
    'EQIX', 'DLR',
    # 상업용
    'SPG', 'O', 'VICI', 'WELL', 'VTR',
    # 주거용
    'AVB', 'EQR', 'MAA', 'ESS', 'UDR', 'INVH', 'CPT',
    # 사무실/기타
    'ARE', 'BXP', 'KIM', 'REG', 'HST', 'FRT', 'WY', 'IRM', 'CBRE',

    # === Consumer Discretionary (경기소비재 - 비기술) ===
    # 레스토랑
    'MCD', 'SBUX', 'YUM', 'CMG', 'DRI',
    # 의류/소매
    'NKE', 'TJX', 'ROST', 'HD', 'LOW', 'BBY', 'ULTA', 'TPR', 'RL', 'PVH', 'VFC',
    # 자동차
    'GM', 'F',
    # 호텔/레저
    'MAR', 'HLT', 'WYNN', 'LVS', 'CZR', 'MGM', 'CCL', 'RCL', 'NCLH',
    # 주택건설
    'DHI', 'LEN', 'NVR', 'PHM',
    # 자동차 부품
    'ORLY', 'AZO', 'GPC', 'BWA', 'APTV',
]

# 중복 제거
VALUE_TICKERS = list(dict.fromkeys(VALUE_TICKERS))


def get_value_list():
    """가치주/배당주 티커 목록 반환"""
    return VALUE_TICKERS.copy()


if __name__ == "__main__":
    tickers = get_value_list()
    print(f"가치주/배당주 종목 수: {len(tickers)}개")

    # 섹터별 카운트
    sectors = {
        'Financials': 57,
        'Healthcare': 35,
        'Consumer Staples': 24,
        'Industrials': 50,
        'Energy': 18,
        'Materials': 22,
        'Utilities': 26,
        'Real Estate': 27,
        'Consumer Discretionary': 30,
    }
    print("\n섹터 구성:")
    for sector, count in sectors.items():
        print(f"  {sector}: ~{count}개")
