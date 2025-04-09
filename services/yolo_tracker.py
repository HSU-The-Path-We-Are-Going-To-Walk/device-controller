import cv2
import requests
from ultralytics import YOLO
from utils.camera import initialize_camera, get_frame
from config import CHATBOT_SERVER
import time
import numpy as np
import threading

model = YOLO("yolov8n.pt")  # 최소 YOLO 모델 사용

# 사람 클래스 ID (YOLO에서 사람은 클래스 0번)
PERSON_CLASS_ID = 0


def count_people(frame):
    # YOLO를 통해 프레임에서 사람 수 계산
    results = model(frame, verbose=False)
    boxes = results[0].boxes
    count = sum(1 for box in boxes if int(box.cls) == PERSON_CLASS_ID)
    return count


def get_detection_frame(frame):
    """
    프레임에서 사람을 감지하고 바운딩 박스를 그립니다.

    Args:
        frame: 카메라에서 캡처한 이미지 프레임

    Returns:
        바운딩 박스가 그려진 프레임
    """
    # 원본 프레임 복사
    detection_frame = frame.copy()

    # YOLO 모델로 객체 감지
    results = model(frame, verbose=False)

    # 결과에서 바운딩 박스 추출
    boxes = results[0].boxes

    # 사람만 필터링하여 바운딩 박스 그리기
    for box in boxes:
        # 클래스 확인 (사람 = 0)
        cls = int(box.cls)
        if cls == PERSON_CLASS_ID:
            # 바운딩 박스 좌표
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # 신뢰도 점수
            conf = float(box.conf[0])

            # 바운딩 박스 그리기 (빨간색)
            cv2.rectangle(detection_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # 신뢰도 점수 표시
            label = f"Person: {conf:.2f}"
            cv2.putText(
                detection_frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2,
            )

    return detection_frame


# 추적 스레드 관리를 위한 변수
tracking_thread = None
is_tracking = False


def track_people():
    """
    카메라로 실시간 인원 추적 후 상태 변화에 따라 서버에 POST 요청 전송
    """
    global tracking_thread, is_tracking

    # 이미 추적 중이면 중복 실행 방지
    if is_tracking:
        print("이미 인원 추적이 실행 중입니다.")
        return

    def tracking_worker():
        global is_tracking
        is_tracking = True

        cap = initialize_camera()
        print("YOLO 인원 추적 시작")

        prev_count = 0

        try:
            while is_tracking:
                frame = get_frame(cap)
                current_count = count_people(frame)

                if prev_count == 0 and current_count > 0:
                    print(f"인원 감지 시작: {current_count}명 → POST /sessionStart")
                    try:
                        requests.post(f"{CHATBOT_SERVER}/sessionStart")
                    except Exception as e:
                        print("/sessionStart 전송 실패:", e)

                elif prev_count > 0 and current_count == 0:
                    print("아무도 없음 → POST /sessionReset")
                    try:
                        requests.post(f"{CHATBOT_SERVER}/sessionReset")
                    except Exception as e:
                        print("/sessionReset 전송 실패:", e)

                prev_count = current_count

                # 너무 자주 요청하지 않도록 약간의 delay
                time.sleep(1)

        except KeyboardInterrupt:
            print("인원 추적 중단됨")
        except Exception as e:
            print(f"인원 추적 중 오류 발생: {e}")
        finally:
            is_tracking = False
            cap.release()
            cv2.destroyAllWindows()

    # 스레드로 실행
    tracking_thread = threading.Thread(target=tracking_worker)
    tracking_thread.daemon = True
    tracking_thread.start()
