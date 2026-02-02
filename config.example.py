"""
API 설정 파일 예시
이 파일을 config.py로 복사하고 API 키를 입력하세요
"""

# ============================================================
# FMP API (선택 사항)
# ============================================================
# FMP API 키 (무료: 250 calls/day)
# 가입: https://financialmodelingprep.com/developer/docs/
# 참고: 현재는 Yahoo Finance를 사용하므로 선택 사항
FMP_API_KEY = "YOUR_API_KEY_HERE"


# ============================================================
# 텔레그램 봇 (필수 - 알림 기능)
# ============================================================
# 텔레그램 봇 토큰
# 1. @BotFather에서 봇 생성: /newbot
# 2. 받은 토큰 입력 (예: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# 텔레그램 채팅 ID
# 1. 봇과 대화 시작 (메시지 1개 전송)
# 2. 브라우저 접속: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# 3. "chat":{"id": 숫자} 찾기 (예: 123456789)
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"


# ============================================================
# 사용 방법
# ============================================================
# 1. 이 파일을 config.py로 복사
#    cp config.example.py config.py (Mac/Linux)
#    copy config.example.py config.py (Windows)
#
# 2. YOUR_BOT_TOKEN_HERE와 YOUR_CHAT_ID_HERE를 실제 값으로 교체
#
# 3. 테스트 실행
#    python telegram_notifier.py
#
# 4. 파일 저장

# ============================================================
# 보안 참고
# ============================================================
# - config.py는 .gitignore에 포함되어 GitHub에 업로드되지 않습니다
# - API 키와 봇 토큰은 절대 공개하지 마세요
# - 토큰이 유출되면 @BotFather에서 재발급하세요
