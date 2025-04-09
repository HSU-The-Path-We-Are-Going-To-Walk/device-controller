from fastapi import APIRouter
from services.webex_call import call_from_device
from services.alert_sender import send_alert
import threading
from pynput import keyboard

router = APIRouter()

def listen_for_button():
    def on_press(key):
        if key == keyboard.Key.enter:
            print("버튼 눌림 인식됨 (Enter)")

            # 시스코 디바이스에서 Webex 화상통화 발신
            #
            # call_from_device()

            # 관리자 시스템에 알림이 뜨도록 POST 요청 전송
            send_alert()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

@router.on_event("startup")
def start_button_listener():
    threading.Thread(target=listen_for_button, daemon=True).start()