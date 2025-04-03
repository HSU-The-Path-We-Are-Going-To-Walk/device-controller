import cv2

def initialize_camera(index=1):
    
    # 윈도우 기준 외장 USB 카메라를 index로 연결
    # 일반적으로 내장 카메라는 index=0, 외장은 1 이상
    
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  

    if not cap.isOpened():
        raise RuntimeError(f"카메라(index={index})를 열 수 없습니다. 연결 상태를 확인하세요.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print(f"카메라(index={index}) 초기화 완료")
    return cap

def get_frame(cap):
    
    # 프레임 한 장 읽어오기
    
    success, frame = cap.read()
    if not success:
        raise RuntimeError("프레임을 읽을 수 없습니다.")
    return frame