@echo off
chcp 65001 > nul
echo ========================================
echo 주식 리포트 자동 업데이트 시작
echo 시간: %date% %time%
echo ========================================

cd /d "%~dp0"

REM Python 실행
python generate_daily_report_v2.py

REM Git 자동 커밋 및 푸시 (선택사항)
REM git add daily_stock_report_*.html index.html
REM git commit -m "Auto update - %date% %time%"
REM git push

echo.
echo ========================================
echo 업데이트 완료!
echo ========================================
