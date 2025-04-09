import cv2
import time

def initialize_camera(index=0):
    
    # macOS에서 웹캠을 연결
    # 테스트 결과 인덱스 2가 작동하는 것으로 확인
    
    cap = cv2.VideoCapture(index)  # macOS에서는 CAP_DSHOW 옵션 제거

    if not cap.isOpened():
        raise RuntimeError(f"카메라(index={index})를 열 수 없습니다. 연결 상태를 확인하세요.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print(f"카메라(index={index}) 초기화 완료")
    return cap

def get_frame(cap, max_retries=3, retry_delay=0.5):
    """
    카메라로부터 프레임 한 장을 읽어옵니다.
    
    Args:
        cap: OpenCV VideoCapture 객체
        max_retries: 읽기 실패 시 최대 재시도 횟수
        retry_delay: 재시도 사이의 대기 시간(초)
    
    Returns:
        읽어온 프레임
        
    Raises:
        RuntimeError: 프레임을 읽을 수 없는 경우
    """
    retry_count = 0
    
    while retry_count < max_retries:
        # 프레임 읽기 시도
        if not cap.isOpened():
            # 카메라가 닫혀 있으면 다시 열기 시도
            print("카메라 연결이 끊어졌습니다. 재연결 시도 중...")
            cap.release()
            cap.open(0)  # 기본 카메라 인덱스 사용
            time.sleep(retry_delay)
            
        success, frame = cap.read()
        
        if success and frame is not None:
            return frame
            
        retry_count += 1
        print(f"프레임 읽기 실패. 재시도 중... ({retry_count}/{max_retries})")
        time.sleep(retry_delay)
    
    # 모든 재시도 실패 시
    raise RuntimeError("카메라로부터 프레임을 읽을 수 없습니다. 카메라 연결 상태를 확인하세요.")