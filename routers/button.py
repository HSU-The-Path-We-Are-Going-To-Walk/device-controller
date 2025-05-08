from fastapi import APIRouter, Request
from services.webex_call import call_from_device
from services.alert_sender import send_alert
import threading
import time
from pynput import keyboard
import requests

router = APIRouter()

# 버튼 입력 처리를 위한 전역 변수
last_press_time = 0
MIN_TIME_BETWEEN_PRESSES = 1.0  # 1초 이내 중복 입력 무시


# 키 입력 이벤트 처리
def on_press(key):
    global last_press_time

    current_time = time.time()

    # 중복 입력 방지 (1초 이내 입력은 무시)
    if current_time - last_press_time < MIN_TIME_BETWEEN_PRESSES:
        return

    last_press_time = current_time

    try:
        # 숫자 키 '1'이 입력되면 /adminCall 엔드포인트로 POST 요청 전송
        if hasattr(key, "char") and key.char == "1":
            print("버튼 눌림 인식됨 (숫자 1)")
            try:
                requests.post("http://localhost:8000/adminCall")
            except Exception as e:
                print("adminCall 요청 실패:", e)
    except AttributeError:
        pass

    return True


# 버튼 리스너 시작
listener = None


def start_button_listener():
    global listener
    try:
        listener = keyboard.Listener(on_press=on_press)
        listener.start()
        print("버튼 리스너가 시작되었습니다.")
    except Exception as e:
        print(f"버튼 리스너 시작 오류: {e}")


def stop_button_listener():
    global listener
    if listener:
        listener.stop()
        listener.join()  # 리소스 정리
        print("버튼 리스너가 종료되었습니다.")


@router.on_event("startup")
def startup_event():
    threading.Thread(target=start_button_listener, daemon=True).start()


@router.on_event("shutdown")
def shutdown_event():
    stop_button_listener()


@router.post("/adminCall")
async def admin_call(request: Request):

    print("POST 요청 수신: /adminCall")

    # 관리자 시스템에 알림이 뜨도록 POST 요청 전송
    send_alert()

    # 시스코 디바이스에서 Webex 화상통화 발신
    call_from_device()
