"""Installation verification script"""

import sys
sys.path.insert(0, 'src')

print("=" * 60)
print("FinanceDataReader Installation Verification")
print("=" * 60)

# 1. Import test
print("\n[1] Import test...")
try:
    import FinanceDataReader as fdr
    print(f"[OK] FinanceDataReader version: {fdr.__version__}")
    print(f"[OK] DataReader function: {hasattr(fdr, 'DataReader')}")
    print(f"[OK] StockListing function: {hasattr(fdr, 'StockListing')}")
    print(f"[OK] SnapDataReader function: {hasattr(fdr, 'SnapDataReader')}")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

# 2. StockListing test
print("\n[2] StockListing test...")
try:
    df = fdr.StockListing('KRX')
    print(f"[OK] KRX stocks count: {len(df)}")
    print(f"[OK] Columns: {list(df.columns)}")
    print(f"\nFirst 5 stocks:")
    print(df.head())
except Exception as e:
    print(f"[FAIL] StockListing failed: {e}")

# 3. SnapDataReader test
print("\n[3] SnapDataReader test...")
try:
    df = fdr.SnapDataReader('KRX/INDEX/LIST')
    print(f"[OK] KRX indexes count: {len(df)}")
    print(f"[OK] Columns: {list(df.columns)}")
    print(f"\nIndex list:")
    print(df)
except Exception as e:
    print(f"[FAIL] SnapDataReader failed: {e}")

# 4. DataReader test
print("\n[4] DataReader test...")
try:
    # Yahoo Finance - Apple (more stable)
    print("- Yahoo Finance (AAPL) test...")
    df = fdr.DataReader('AAPL', '2023-01-01', '2023-01-31', data_source='YAHOO')
    if not df.empty:
        print(f"  [OK] Data rows: {len(df)}")
        print(f"  [OK] Columns: {list(df.columns)}")
        print(f"\n  First 3 rows:")
        print(df.head(3))
    else:
        print("  [WARN] Yahoo Finance API call failed (network issue possible)")

except Exception as e:
    print(f"  [FAIL] DataReader failed: {e}")

# 5. Data source auto-detection test
print("\n[5] Data source auto-detection test...")
try:
    from FinanceDataReader.data import _detect_data_source

    tests = [
        ('005930', 'NAVER'),  # Korean stock
        ('AAPL', 'YAHOO'),    # US stock
        ('BTC/USD', 'CRYPTO'), # Crypto
        ('KS11', 'NAVER'),     # Korean index
    ]

    for symbol, expected in tests:
        detected = _detect_data_source(symbol)
        status = "[OK]" if detected == expected else "[FAIL]"
        print(f"  {status} {symbol} -> {detected} (expected: {expected})")

except Exception as e:
    print(f"  [FAIL] Auto-detection test failed: {e}")

# Complete
print("\n" + "=" * 60)
print("Verification completed!")
print("=" * 60)
print("\nUsage example:")
print("  import FinanceDataReader as fdr")
print("  df = fdr.DataReader('AAPL', '2023')")
print("  df_krx = fdr.StockListing('KRX')")
print("=" * 60)
