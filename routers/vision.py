from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from services.yolo_tracker import track_people, get_detection_frame
from utils.camera import initialize_camera, get_frame
import cv2
import io
import time

router = APIRouter()


@router.on_event("startup")
def start_tracking():
    track_people()


@router.get("/stream/detection")
async def video_feed():
    """
    YOLO로 사람을 감지하고 바운딩 박스를 그린 비디오 스트림을 제공합니다.
    """
    return StreamingResponse(
        generate_frames(), media_type="multipart/x-mixed-replace;boundary=frame"
    )


def generate_frames():
    """
    YOLO 감지 결과가 포함된 비디오 프레임을 생성하는 제너레이터 함수
    """
    cap = initialize_camera()  # 프로젝트의 카메라 초기화 함수 사용
    try:
        while True:
            try:
                # 프로젝트의 프레임 가져오기 함수 사용
                frame = get_frame(cap)

                # YOLO 감지 및 바운딩 박스 그리기 적용
                frame_with_detection = get_detection_frame(frame)

                # JPEG 형식으로 인코딩
                _, encoded_frame = cv2.imencode(".jpg", frame_with_detection)
                frame_bytes = encoded_frame.tobytes()

                # multipart 응답 형식으로 전송
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                )

                # 프레임 레이트 조절
                time.sleep(0.05)  # 약 20fps
            except Exception as e:
                print(f"프레임 생성 중 오류 발생: {e}")
                time.sleep(0.5)  # 오류 발생 시 잠시 대기
                continue
    finally:
        cap.release()
