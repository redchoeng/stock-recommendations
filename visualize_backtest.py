"""
백테스팅 결과 시각화
차트 자동 생성 및 HTML 리포트
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
from collections import Counter
import re

# 한글 폰트 설정 (Windows)
matplotlib.rc('font', family='Malgun Gothic')
matplotlib.rc('axes', unicode_minus=False)

# CSV 파일 읽기
print("=" * 60)
print("         백테스팅 결과 시각화")
print("=" * 60)
print()

# 최신 파일 찾기
import glob
csv_files = glob.glob("backtest_result_*.csv")
if not csv_files:
    print("⚠️  백테스팅 결과 파일이 없습니다.")
    exit()

latest_file = max(csv_files)
print(f"파일: {latest_file}")
print()

df = pd.read_csv(latest_file)
df['date'] = pd.to_datetime(df['date'])

# 통계
initial_capital = 100000
final_capital = df['capital'].iloc[-1]
total_return = (final_capital - initial_capital) / initial_capital

print(f"초기 자본: ${initial_capital:,.0f}")
print(f"최종 자본: ${final_capital:,.0f}")
print(f"총 수익률: {total_return*100:+.2f}%")
print()

# 1. 누적 자본 추이 차트
print("[Chart 1] Capital Growth")
plt.figure(figsize=(14, 6))
plt.plot(df['date'], df['capital'], linewidth=2, color='#2E86AB', label='전략')
plt.axhline(y=initial_capital, color='gray', linestyle='--', alpha=0.5, label='초기 자본')
plt.fill_between(df['date'], initial_capital, df['capital'],
                 where=(df['capital'] >= initial_capital),
                 color='green', alpha=0.1, label='수익')
plt.fill_between(df['date'], initial_capital, df['capital'],
                 where=(df['capital'] < initial_capital),
                 color='red', alpha=0.1, label='손실')

plt.title('누적 자본 추이 (1년)', fontsize=16, fontweight='bold')
plt.xlabel('날짜', fontsize=12)
plt.ylabel('자본 ($)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=10)
plt.tight_layout()
plt.savefig('chart1_capital.png', dpi=300, bbox_inches='tight')
print("  [OK] chart1_capital.png")
plt.close()

# 2. 주간 수익률 막대 그래프
print("[Chart 2] Weekly Returns")
plt.figure(figsize=(14, 6))
colors = ['green' if r > 0 else 'red' for r in df['return']]
plt.bar(range(len(df)), df['return'] * 100, color=colors, alpha=0.7)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

plt.title('주간 수익률 (%)', fontsize=16, fontweight='bold')
plt.xlabel('주차', fontsize=12)
plt.ylabel('수익률 (%)', fontsize=12)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('chart2_returns.png', dpi=300, bbox_inches='tight')
print("  [OK] chart2_returns.png")
plt.close()

# 3. 종목 선정 빈도
print("[Chart 3] Stock Frequency")
all_stocks = []
for stocks_str in df['top_stocks']:
    # 문자열에서 종목 추출
    stocks = re.findall(r"'([A-Z-]+)'", stocks_str)
    all_stocks.extend(stocks)

stock_counts = Counter(all_stocks)
top_10_stocks = stock_counts.most_common(10)

stocks = [s[0] for s in top_10_stocks]
counts = [s[1] for s in top_10_stocks]

plt.figure(figsize=(12, 7))
bars = plt.barh(stocks[::-1], counts[::-1], color='#A23B72')
plt.xlabel('선정 횟수', fontsize=12)
plt.title('TOP 10 종목 선정 빈도', fontsize=16, fontweight='bold')
plt.grid(True, alpha=0.3, axis='x')

# 막대에 숫자 표시
for bar, count in zip(bars, counts[::-1]):
    plt.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f'{count}회', va='center', fontsize=10)

plt.tight_layout()
plt.savefig('chart3_stocks.png', dpi=300, bbox_inches='tight')
print("  [OK] chart3_stocks.png")
plt.close()

# 4. 수익률 분포 히스토그램
print("[Chart 4] Return Distribution")
plt.figure(figsize=(10, 6))
plt.hist(df['return'] * 100, bins=20, color='#F18F01', alpha=0.7, edgecolor='black')
plt.axvline(x=0, color='red', linestyle='--', linewidth=2, label='손익 분기점')
plt.axvline(x=df['return'].mean() * 100, color='green', linestyle='--',
            linewidth=2, label=f'평균: {df["return"].mean()*100:.2f}%')

plt.title('수익률 분포', fontsize=16, fontweight='bold')
plt.xlabel('수익률 (%)', fontsize=12)
plt.ylabel('빈도', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('chart4_distribution.png', dpi=300, bbox_inches='tight')
print("  [OK] chart4_distribution.png")
plt.close()

# 5. 월별 수익률
print("[Chart 5] Monthly Returns")
df['month'] = df['date'].dt.to_period('M')
monthly_returns = df.groupby('month')['return'].sum() * 100

plt.figure(figsize=(12, 6))
colors_monthly = ['green' if r > 0 else 'red' for r in monthly_returns]
plt.bar(range(len(monthly_returns)), monthly_returns, color=colors_monthly, alpha=0.7)
plt.xticks(range(len(monthly_returns)),
           [str(m) for m in monthly_returns.index], rotation=45)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

plt.title('월별 누적 수익률 (%)', fontsize=16, fontweight='bold')
plt.xlabel('월', fontsize=12)
plt.ylabel('수익률 (%)', fontsize=12)
plt.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('chart5_monthly.png', dpi=300, bbox_inches='tight')
print("  [OK] chart5_monthly.png")
plt.close()

# 6. Drawdown (낙폭) 차트
print("[Chart 6] Drawdown")
capital_series = df['capital']
peak = capital_series.expanding(min_periods=1).max()
drawdown = (capital_series - peak) / peak * 100

plt.figure(figsize=(14, 6))
plt.fill_between(df['date'], 0, drawdown, color='red', alpha=0.3)
plt.plot(df['date'], drawdown, color='darkred', linewidth=2)

plt.title('낙폭 (Drawdown) - 고점 대비 하락률', fontsize=16, fontweight='bold')
plt.xlabel('날짜', fontsize=12)
plt.ylabel('낙폭 (%)', fontsize=12)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('chart6_drawdown.png', dpi=300, bbox_inches='tight')
print("  [OK] chart6_drawdown.png")
plt.close()

# HTML 리포트 생성
print()
print("[HTML] Generating report...")

html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>백테스팅 결과 리포트</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .chart-section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .chart-section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .chart-section img {{
            width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        .top-stocks {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stock-badge {{
            background: #667eea;
            color: white;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 퀀트 전략 백테스팅 결과</h1>
        <p>1년 백테스팅 (2025.02 - 2026.02)</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-label">초기 자본</div>
            <div class="stat-value">${initial_capital:,.0f}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">최종 자본</div>
            <div class="stat-value">${final_capital:,.0f}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">총 수익률</div>
            <div class="stat-value" style="color: {'green' if total_return > 0 else 'red'};">
                {total_return*100:+.2f}%
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-label">승률</div>
            <div class="stat-value">{(df['return'] > 0).sum() / len(df) * 100:.1f}%</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">최대 낙폭</div>
            <div class="stat-value" style="color: red;">{drawdown.min():.2f}%</div>
        </div>
    </div>

    <div class="chart-section">
        <h2>📈 누적 자본 추이</h2>
        <img src="chart1_capital.png" alt="누적 자본">
    </div>

    <div class="chart-section">
        <h2>📊 주간 수익률</h2>
        <img src="chart2_returns.png" alt="주간 수익률">
    </div>

    <div class="chart-section">
        <h2>🏆 TOP 10 종목</h2>
        <img src="chart3_stocks.png" alt="종목 빈도">
        <div class="top-stocks">
            {"".join([f'<div class="stock-badge">{s[0]}<br>{s[1]}회</div>' for s in top_10_stocks])}
        </div>
    </div>

    <div class="chart-section">
        <h2>📉 수익률 분포</h2>
        <img src="chart4_distribution.png" alt="수익률 분포">
    </div>

    <div class="chart-section">
        <h2>📅 월별 수익률</h2>
        <img src="chart5_monthly.png" alt="월별 수익률">
    </div>

    <div class="chart-section">
        <h2>⚠️ 낙폭 (Drawdown)</h2>
        <img src="chart6_drawdown.png" alt="Drawdown">
    </div>

    <div class="chart-section">
        <h2>📋 종목 선정 통계</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <thead>
                <tr style="background: #f0f0f0;">
                    <th style="padding: 10px; border: 1px solid #ddd;">순위</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">종목</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">선정 횟수</th>
                    <th style="padding: 10px; border: 1px solid #ddd;">비율</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f'''
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{i+1}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; font-weight: bold;">{s[0]}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{s[1]}</td>
                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{s[1]/len(df)*100:.1f}%</td>
                </tr>
                ''' for i, s in enumerate(top_10_stocks[:10])])}
            </tbody>
        </table>
    </div>

    <div style="text-align: center; padding: 30px; color: #666;">
        <p>생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>🚀 Powered by 검증된 퀀트 전략</p>
    </div>
</body>
</html>
"""

with open('backtest_report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("  [OK] backtest_report.html")
print()

print("=" * 60)
print("VISUALIZATION COMPLETE!")
print("=" * 60)
print()
print("Created files:")
print("  [PNG] chart1_capital.png - Capital Growth")
print("  [PNG] chart2_returns.png - Weekly Returns")
print("  [PNG] chart3_stocks.png - Stock Frequency")
print("  [PNG] chart4_distribution.png - Return Distribution")
print("  [PNG] chart5_monthly.png - Monthly Returns")
print("  [PNG] chart6_drawdown.png - Drawdown")
print("  [HTML] backtest_report.html - Full Report")
print()
print("Opening HTML report in browser...")

import os
os.system('start backtest_report.html')
