import httpx
from config import ADMIN_SERVER, BUS_STOP_ID

def send_alert():
    url = f"{ADMIN_SERVER}/api/simulate-emergency/{BUS_STOP_ID}"
    try:
        response = httpx.post(url)

        print(f"관리자 시스템에 비상 알림 전송 완료: {response.status_code}")
    except Exception as e:
        print("비상 알림 전송 실패:", e)