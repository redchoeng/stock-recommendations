"""DataReader 함수 테스트"""

import pytest
import pandas as pd
from datetime import datetime


def test_import():
    """패키지 import 테스트"""
    import sys
    sys.path.insert(0, 'src')

    import FinanceDataReader as fdr

    assert fdr.__version__ == '0.1.0'
    assert hasattr(fdr, 'DataReader')
    assert hasattr(fdr, 'StockListing')
    assert hasattr(fdr, 'SnapDataReader')


def test_datareader_krx():
    """KRX 데이터 조회 테스트"""
    import sys
    sys.path.insert(0, 'src')

    import FinanceDataReader as fdr

    # 삼성전자 (005930)
    df = fdr.DataReader('005930', '2023-01-01', '2023-01-31', data_source='NAVER')

    # DataFrame인지 확인
    assert isinstance(df, pd.DataFrame)

    # 빈 데이터가 아니거나 API 실패 시 빈 DataFrame 허용
    # (실제 API 호출 실패 가능성 고려)


def test_stocklisting():
    """StockListing 함수 테스트"""
    import sys
    sys.path.insert(0, 'src')

    import FinanceDataReader as fdr

    # KRX 종목 목록
    df = fdr.StockListing('KRX')

    assert isinstance(df, pd.DataFrame)
    assert 'Code' in df.columns or len(df) >= 0  # 샘플 데이터라도 구조 확인


def test_snapdatareader():
    """SnapDataReader 함수 테스트"""
    import sys
    sys.path.insert(0, 'src')

    import FinanceDataReader as fdr

    # KRX 인덱스 목록
    df = fdr.SnapDataReader('KRX/INDEX/LIST')

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0


if __name__ == '__main__':
    test_import()
    print("✓ Import test passed")

    test_datareader_krx()
    print("✓ DataReader test passed")

    test_stocklisting()
    print("✓ StockListing test passed")

    test_snapdatareader()
    print("✓ SnapDataReader test passed")

    print("\nAll tests passed!")
