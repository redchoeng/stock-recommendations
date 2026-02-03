"""
S&P 500 종목 목록 (2024년 기준)
"""

SP500_TICKERS = [
    # Technology
    'AAPL', 'MSFT', 'NVDA', 'AVGO', 'ORCL', 'CRM', 'AMD', 'ADBE', 'CSCO', 'ACN',
    'IBM', 'INTU', 'QCOM', 'TXN', 'AMAT', 'NOW', 'PANW', 'MU', 'ADI', 'LRCX',
    'INTC', 'KLAC', 'SNPS', 'CDNS', 'MCHP', 'FTNT', 'ANET', 'APH', 'TEL', 'MSI',
    'NXPI', 'ON', 'HPQ', 'KEYS', 'CDW', 'TYL', 'FSLR', 'ZBRA', 'TER',
    'NTAP', 'SWKS', 'TRMB', 'PTC', 'GEN', 'AKAM', 'WDC', 'EPAM', 'FFIV',

    # Communication Services
    'GOOGL', 'GOOG', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS', 'CHTR',
    'EA', 'WBD', 'OMC', 'TTWO', 'MTCH', 'FOXA', 'FOX', 'NWS', 'NWSA',
    'LYV',

    # Consumer Discretionary
    'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'LOW', 'SBUX', 'TJX', 'BKNG', 'ABNB',
    'CMG', 'ORLY', 'AZO', 'MAR', 'GM', 'F', 'HLT', 'ROST', 'DHI', 'YUM',
    'EBAY', 'LEN', 'NVR', 'GRMN', 'PHM', 'ULTA', 'POOL', 'GPC', 'TSCO', 'DRI',
    'LVS', 'WYNN', 'CZR', 'MGM', 'BWA', 'APTV', 'HAS', 'TPR', 'EXPE', 'CCL',
    'RCL', 'NCLH', 'RL', 'VFC', 'PVH', 'BBY',

    # Consumer Staples
    'WMT', 'PG', 'COST', 'KO', 'PEP', 'PM', 'MO', 'MDLZ', 'CL', 'GIS',
    'KMB', 'SYY', 'STZ', 'KHC', 'KR', 'HSY', 'MKC', 'MNST', 'ADM', 'CAG',
    'K', 'CLX', 'TSN', 'TAP', 'CPB', 'SJM', 'HRL', 'CHD', 'BF-B', 'LW',

    # Healthcare
    'LLY', 'UNH', 'JNJ', 'MRK', 'ABBV', 'TMO', 'ABT', 'DHR', 'PFE', 'BMY',
    'AMGN', 'ISRG', 'ELV', 'GILD', 'VRTX', 'SYK', 'MDT', 'CI', 'REGN', 'CVS',
    'BSX', 'ZTS', 'BDX', 'MCK', 'HCA', 'EW', 'IDXX', 'A', 'DXCM', 'IQV',
    'MTD', 'GEHC', 'RMD', 'HUM', 'BIIB', 'ILMN', 'CAH', 'WST', 'ZBH', 'COR',
    'MOH', 'BAX', 'HOLX', 'CNC', 'ALGN', 'DGX', 'LH', 'RVTY', 'VTRS', 'TFX',
    'INCY', 'TECH', 'MRNA', 'XRAY', 'HSIC',

    # Financials
    'BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'GS', 'MS', 'SPGI', 'BLK',
    'SCHW', 'C', 'AXP', 'MMC', 'PGR', 'CB', 'ICE', 'CME', 'USB', 'AON',
    'PNC', 'TFC', 'MET', 'AIG', 'AFL', 'PRU', 'MCO', 'MSCI', 'TRV', 'AJG',
    'ALL', 'AMP', 'FITB', 'COF', 'BK', 'STT', 'CINF', 'NDAQ', 'RJF', 'MTB',
    'WRB', 'HBAN', 'RF', 'CFG', 'NTRS', 'KEY', 'FDS', 'EG', 'L',
    'BRO', 'CBOE', 'GL', 'AIZ', 'JKHY', 'IVZ', 'BEN', 'ZION',

    # Industrials
    'GE', 'CAT', 'RTX', 'HON', 'UNP', 'BA', 'UPS', 'DE', 'LMT', 'ADP',
    'NOC', 'GD', 'ETN', 'ITW', 'WM', 'CSX', 'EMR', 'NSC', 'MMM', 'PH',
    'CTAS', 'FDX', 'JCI', 'TT', 'PCAR', 'CARR', 'CPRT', 'GWW', 'OTIS', 'CMI',
    'ODFL', 'AME', 'RSG', 'FAST', 'VRSK', 'ROK', 'URI', 'PWR', 'PAYX', 'IR',
    'XYL', 'DOV', 'HWM', 'WAB', 'LHX', 'DAL', 'HII', 'GPN', 'J', 'LDOS',
    'EFX', 'TDG', 'SWK', 'ROP', 'IEX', 'BR', 'EXPD', 'NDSN', 'FTV', 'MAS',
    'PNR', 'UAL', 'CHRW', 'JBHT', 'CSGP', 'ALLE', 'SNA', 'LUV',
    'PAYC', 'AAL', 'GNRC', 'AXON',

    # Energy
    'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY',
    'WMB', 'KMI', 'BKR', 'HAL', 'DVN', 'FANG', 'OKE', 'CTRA', 'TRGP',
    'APA',

    # Materials
    'LIN', 'APD', 'SHW', 'ECL', 'FCX', 'NUE', 'NEM', 'VMC', 'MLM', 'DOW',
    'DD', 'PPG', 'CTVA', 'IFF', 'ALB', 'EMN', 'BALL', 'CF', 'FMC', 'LYB',
    'IP', 'PKG', 'AVY', 'MOS', 'AMCR', 'CE', 'SEE',

    # Utilities
    'NEE', 'SO', 'DUK', 'CEG', 'SRE', 'AEP', 'D', 'PCG', 'EXC', 'XEL',
    'ED', 'PEG', 'WEC', 'AWK', 'ES', 'EIX', 'DTE', 'ETR', 'PPL', 'AEE',
    'FE', 'CMS', 'AES', 'LNT', 'EVRG', 'CNP', 'NI', 'ATO', 'NRG', 'PNW',

    # Real Estate
    'PLD', 'AMT', 'EQIX', 'PSA', 'WELL', 'SPG', 'DLR', 'CCI', 'O', 'VICI',
    'SBAC', 'AVB', 'EQR', 'WY', 'CBRE', 'VTR', 'ARE', 'EXR', 'MAA', 'IRM',
    'ESS', 'INVH', 'UDR', 'KIM', 'REG', 'HST', 'BXP', 'CPT', 'FRT',
]

def get_sp500_list():
    """S&P 500 티커 목록 반환"""
    return SP500_TICKERS.copy()
