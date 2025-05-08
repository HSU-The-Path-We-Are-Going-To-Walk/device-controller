import subprocess
import socket
import os
import time
from config import DEVICE_IP, USERNAME, PASSWORD, TARGET_EMAIL

# 스크립트 경로를 고정값으로 설정 (홈 디렉토리)
SCRIPT_PATH = os.path.expanduser("~/webex_call_script.sh")


def check_host_connection(host, port=443, timeout=2):
    """호스트 연결 가능성을 확인합니다"""
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True
    except Exception as e:
        print(f"호스트 연결 확인 실패: {e}")
        return False


# 시스코 디바이스에서 Webex 화상통화 발신
def call_from_device():
    url = f"https://{DEVICE_IP}/putxml"

    # XML 페이로드 생성
    payload = f'<?xml version="1.0" encoding="UTF-8"?><Command><Dial><Number>{TARGET_EMAIL}</Number></Dial></Command>'

    # 임시 스크립트 파일 생성 (고정 경로)
    with open(SCRIPT_PATH, "w") as f:
        f.write(
            f"""#!/bin/bash
curl -k -s -u {USERNAME}:{PASSWORD} -X POST {url} -H "Content-Type: text/xml" -d '{payload}'
# -s 옵션 추가로 curl 출력을 조용하게 만듦
"""
        )

    try:
        # 권한 설정
        os.chmod(SCRIPT_PATH, 0o755)

        # 터미널에서 스크립트 실행 (백그라운드로 실행하고 즉시 종료)
        terminal_cmd = f"""
        osascript -e 'tell application "Terminal"
            set currentTab to do script "bash {SCRIPT_PATH}; exit"
            delay 0.5
            set visible of window 1 to false
        end tell'
        """

        print("백그라운드에서 명령 실행 중...")
        result = subprocess.run(
            terminal_cmd, shell=True, capture_output=True, text=True
        )

        # 결과 확인
        if result.returncode == 0:
            print("시스코 디바이스에서 Webex 화상통화 발신 요청 성공")
        else:
            print(f"시스코 디바이스에서 Webex 화상통화 발신 실패: {result.stderr}")
            if result.stdout:
                print(f"출력: {result.stdout}")

        # 파일은 삭제하지 않고 유지 (직접 실행 가능하도록)

    except Exception as e:
        print(f"시스코 디바이스에서 Webex 화상통화 발신 오류: {e}")
