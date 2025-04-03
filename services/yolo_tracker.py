import cv2
import requests
from ultralytics import YOLO
from utils.camera import initialize_camera, get_frame
from config import SERVER
import time

model = YOLO("yolov8n.pt")  # 최소 YOLO 모델 사용

# 사람 클래스 ID (YOLO에서 사람은 클래스 0번)
PERSON_CLASS_ID = 0

def count_people(frame):

    # YOLO를 통해 프레임에서 사람 수 계산
    results = model(frame, verbose=False)
    boxes = results[0].boxes
    count = sum(1 for box in boxes if int(box.cls) == PERSON_CLASS_ID)
    return count

def track_people():

    # 카메라로 실시간 인원 추적 후 상태 변화에 따라 서버에 POST 요청 전송
    cap = initialize_camera()
    print("YOLO 인원 추적 시작")

    prev_count = 0

    try:
        while True:
            frame = get_frame(cap)
            current_count = count_people(frame)

            if prev_count == 0 and current_count > 0:
                print(f"인원 감지 시작: {current_count}명 → POST /sessionStart")
                try:
                    requests.post(f"{SERVER}/sessionStart")
                except Exception as e:
                    print("/sessionStart 전송 실패:", e)

            elif prev_count > 0 and current_count == 0:
                print("아무도 없음 → POST /sessionReset")
                try:
                    requests.post(f"{SERVER}/sessionReset")
                except Exception as e:
                    print("/sessionReset 전송 실패:", e)

            prev_count = current_count

            # 너무 자주 요청하지 않도록 약간의 delay
            time.sleep(1)

    except KeyboardInterrupt:
        print("인원 추적 중단됨")

    finally:
        cap.release()
        cv2.destroyAllWindows()