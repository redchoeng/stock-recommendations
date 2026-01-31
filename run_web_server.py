"""
주식 추천 웹 서버
외부에서 접속 가능한 웹 서버 실행

사용법:
    python run_web_server.py

접속:
    로컬: http://localhost:8000
    외부: http://[당신의IP주소]:8000
"""

import http.server
import socketserver
import os
import subprocess
from datetime import datetime


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """커스텀 HTTP 핸들러"""

    def do_GET(self):
        """GET 요청 처리"""
        # 루트 경로 요청시 최신 리포트로 리다이렉트
        if self.path == '/':
            # 가장 최신 리포트 파일 찾기
            report_files = [f for f in os.listdir('.') if f.startswith('daily_stock_report_') and f.endswith('.html')]
            if report_files:
                latest_report = sorted(report_files)[-1]
                self.path = '/' + latest_report
            else:
                self.send_error(404, "리포트 파일이 없습니다. generate_daily_report_v2.py를 먼저 실행하세요.")
                return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        """CORS 헤더 추가"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()


def get_local_ip():
    """로컬 IP 주소 가져오기"""
    import socket
    try:
        # 외부 연결을 통해 로컬 IP 확인
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"


def main():
    PORT = 8000
    local_ip = get_local_ip()

    print("\n" + "="*70)
    print("주식 추천 웹 서버 시작")
    print("="*70 + "\n")

    # 작업 디렉토리 확인
    print(f"작업 디렉토리: {os.getcwd()}\n")

    # 리포트 파일 확인
    report_files = [f for f in os.listdir('.') if f.startswith('daily_stock_report_') and f.endswith('.html')]
    if report_files:
        latest_report = sorted(report_files)[-1]
        print(f"[OK] 최신 리포트: {latest_report}")
    else:
        print("[WARNING] 리포트 파일이 없습니다!")
        print("먼저 다음 명령을 실행하세요:")
        print("  python generate_daily_report_v2.py\n")

    print(f"\n서버 실행 중...\n")
    print("접속 주소:")
    print(f"  로컬: http://localhost:{PORT}")
    print(f"  내부망: http://{local_ip}:{PORT}")
    print(f"\n외부 접속 (포트포워딩 필요):")
    print(f"  1. 공유기 설정에서 포트 {PORT}을 포트포워딩")
    print(f"  2. 공인 IP 확인: https://www.whatismyip.com/")
    print(f"  3. http://[공인IP]:{PORT} 으로 접속\n")
    print("="*70)
    print("서버 중지: Ctrl+C")
    print("="*70 + "\n")

    # 서버 시작
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 서버 대기 중...\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[종료] 서버를 종료합니다.")
    except Exception as e:
        print(f"\n[오류] {e}")


if __name__ == "__main__":
    main()
