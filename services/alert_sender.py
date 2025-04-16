import httpx
from config import ADMIN_SERVER, BUS_STOP_ID

def send_alert():
    url = f"{ADMIN_SERVER}/api/simulate-emergency/{BUS_STOP_ID}"
    try:
        print(f"Request URL: {url}")  # 요청 URL 출력
        response = httpx.post(url)

        # 응답 상태 코드와 내용 출력
        print(f"Response Status: {response.status_code}")
        print(f"Response Content: {response.text}")

        if response.status_code == 404:
            print("404 Not Found: 요청한 URL이 서버에서 존재하지 않습니다.")
        else:
            print(f"관리자 시스템에 비상 알림 전송 완료: {response.status_code}")
    except Exception as e:
        print("비상 알림 전송 실패:", e)