from fastapi import APIRouter, Request
from services.webex_call import call_from_device
from services.alert_sender import send_alert
import threading
from pynput import keyboard

router = APIRouter()

listener = None  # 리스너를 전역 변수로 선언

def listen_for_button():
    def on_press(key):
        if key == keyboard.KeyCode.from_char('1'):  # 숫자 1 키를 감지
            print("버튼 눌림 인식됨 (숫자 1)")

            # 시스코 디바이스에서 Webex 화상통화 발신
            call_from_device()

            # 관리자 시스템에 알림이 뜨도록 POST 요청 전송
            send_alert()

    global listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # 데몬 스레드로 실행

@router.on_event("startup")
def start_button_listener():
    threading.Thread(target=listen_for_button, daemon=True).start()

@router.on_event("shutdown")
def stop_button_listener():
    global listener
    if listener:
        listener.stop()  # 리스너 정지
        listener.join()  # 리소스 정리

@router.post("/adminCall")
async def admin_call(request: Request):

    print("POST 요청 수신: /adminCall")

    # 시스코 디바이스에서 Webex 화상통화 발신
    call_from_device()

    # 관리자 시스템에 알림이 뜨도록 POST 요청 전송
    send_alert()