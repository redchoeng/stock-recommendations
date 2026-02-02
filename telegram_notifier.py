"""
텔레그램 알림 모듈
주식 추천 및 시장 변화 알림 전송
"""

import requests
import json
from datetime import datetime


class TelegramNotifier:
    """텔레그램 봇 알림 클래스"""

    def __init__(self, bot_token, chat_id):
        """
        Args:
            bot_token: 텔레그램 봇 토큰
            chat_id: 텔레그램 채팅 ID
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, message, parse_mode='HTML'):
        """
        텔레그램 메시지 전송

        Args:
            message: 전송할 메시지
            parse_mode: 메시지 포맷 ('HTML' or 'Markdown')
        """
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                print(f"[OK] 텔레그램 메시지 전송 성공")
                return True
            else:
                print(f"[ERROR] 텔레그램 전송 실패: {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            print(f"[ERROR] 텔레그램 전송 오류: {e}")
            return False

    def send_rebalance_report(self, stocks, performance):
        """
        리밸런싱 보고서 전송

        Args:
            stocks: 추천 종목 리스트 [{'ticker': 'AAPL', 'score': 85.5, ...}, ...]
            performance: 성과 정보 {'return': 0.0343, 'sharpe': 4.49, ...}
        """
        date = datetime.now().strftime('%Y-%m-%d')

        message = f"""
🔄 <b>리밸런싱 알림</b> ({date})

📊 <b>추천 종목 TOP 10</b>
"""

        for i, stock in enumerate(stocks[:10], 1):
            ticker = stock.get('ticker', 'N/A')
            score = stock.get('total_score', 0)
            tech = stock.get('tech_score', 0)
            news = stock.get('news_score', 0)

            message += f"{i}. <b>{ticker}</b> (점수: {score:.1f})\n"
            message += f"   기술: {tech:.1f}/75, 뉴스: {news:.1f}/20\n"

        message += f"""
📈 <b>전략 성과</b>
수익률: {performance.get('return', 0)*100:+.2f}%
샤프 비율: {performance.get('sharpe', 0):.2f}
승률: {performance.get('win_rate', 0)*100:.1f}%

🔗 <a href="https://redchoeng.github.io/stock-recommendations/">상세 보고서 확인</a>
"""

        return self.send_message(message)

    def send_market_alert(self, alert_type, details):
        """
        시장 급변 알림 전송

        Args:
            alert_type: 알림 타입 ('crash', 'surge', 'volatility', 'news')
            details: 상세 정보 딕셔너리
        """
        icons = {
            'crash': '🔴',
            'surge': '🟢',
            'volatility': '⚠️',
            'news': '📰'
        }

        titles = {
            'crash': '급락 경고',
            'surge': '급등 알림',
            'volatility': '변동성 급증',
            'news': '뉴스 감성 급변'
        }

        icon = icons.get(alert_type, '🚨')
        title = titles.get(alert_type, '시장 알림')
        date = datetime.now().strftime('%Y-%m-%d %H:%M')

        message = f"""
{icon} <b>{title}</b> ({date})

{details.get('description', '시장에 급격한 변화가 감지되었습니다.')}

<b>현재 상황:</b>
"""

        if 'spy_change' in details:
            message += f"S&P500: {details['spy_change']:+.2f}%\n"

        if 'vix' in details:
            message += f"VIX: {details['vix']:.1f} (변동성)\n"

        if 'recommended_action' in details:
            message += f"\n<b>권장 조치:</b>\n{details['recommended_action']}\n"

        message += f"""
🔗 <a href="https://redchoeng.github.io/stock-recommendations/">실시간 분석 확인</a>
"""

        return self.send_message(message)

    def send_daily_summary(self, summary):
        """
        일일 시장 요약 전송

        Args:
            summary: 요약 정보 {'spy_change': 0.012, 'top_stocks': [...], ...}
        """
        date = datetime.now().strftime('%Y-%m-%d')

        spy_change = summary.get('spy_change', 0)
        icon = '🟢' if spy_change > 0 else '🔴'

        message = f"""
📊 <b>일일 시장 요약</b> ({date})

{icon} S&P500: {spy_change:+.2f}%
📈 VIX: {summary.get('vix', 0):.1f}

<b>TOP 3 종목:</b>
"""

        for i, stock in enumerate(summary.get('top_stocks', [])[:3], 1):
            ticker = stock.get('ticker', 'N/A')
            score = stock.get('score', 0)
            message += f"{i}. {ticker} ({score:.1f}점)\n"

        message += f"""
🔗 <a href="https://redchoeng.github.io/stock-recommendations/">전체 보고서</a>
"""

        return self.send_message(message)


# 텔레그램 봇 설정 가이드
SETUP_GUIDE = """
텔레그램 봇 설정 방법:

1. BotFather로 봇 생성
   - 텔레그램에서 @BotFather 검색
   - /newbot 명령 입력
   - 봇 이름 설정
   - 봇 토큰 받기 (예: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)

2. Chat ID 찾기
   - 봇과 대화 시작 (메시지 1개 전송)
   - 브라우저에서 접속: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   - "chat":{"id": 숫자} 찾기 (예: 123456789)

3. config.py에 추가
   TELEGRAM_BOT_TOKEN = "your_bot_token"
   TELEGRAM_CHAT_ID = "your_chat_id"

4. 테스트
   python telegram_notifier.py
"""


if __name__ == '__main__':
    print("=" * 60)
    print("         텔레그램 알림 테스트")
    print("=" * 60)
    print()

    # config.py에서 설정 불러오기
    try:
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

        notifier = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)

        # 테스트 메시지 전송
        print("[1] 테스트 메시지 전송...")
        test_message = """
🎉 <b>텔레그램 알림 설정 완료!</b>

주식 추천 봇이 정상 작동합니다.

앞으로 다음 알림을 받게 됩니다:
✅ 14일 리밸런싱 결과
🚨 시장 급변 알림
📊 일일 시장 요약

🔗 <a href="https://redchoeng.github.io/stock-recommendations/">보고서 바로가기</a>
"""

        if notifier.send_message(test_message):
            print()
            print("=" * 60)
            print("✅ 설정 완료!")
            print("텔레그램에서 메시지를 확인하세요.")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("❌ 전송 실패")
            print("config.py에서 토큰과 Chat ID를 확인하세요.")
            print("=" * 60)

    except ImportError:
        print("[ERROR] config.py에 텔레그램 설정이 없습니다.")
        print()
        print(SETUP_GUIDE)
