import cv2
import time
import platform
import os
import subprocess

# 설정 값을 저장할 딕셔너리
CAMERA_CONFIG = {
    "windows": {"index": None, "use_dshow": True},
    "darwin": {"index": None, "use_dshow": False},  # macOS는 'darwin'으로 표시됨
}


def detect_webcam():
    """
    사용 가능한 웹캠을 감지하고 가장 적합한 인덱스를 반환합니다.

    Returns:
        웹캠으로 인식된 카메라 인덱스 목록
    """
    system = platform.system().lower()
    print(f"운영체제 {system}에서 사용 가능한 웹캠을 검색합니다...")

    # 사용 가능한 카메라 인덱스와 정보를 저장할 리스트
    available_cameras = []

    # 내장 또는 USB 웹캠을 식별하기 위한 키워드
    webcam_keywords = [
        "webcam",
        "camera",
        "cam",
        "facetime",
        "hd camera",
        "integrated camera",
    ]

    # macOS에서 외부 명령어로 카메라 정보 얻기
    if system == "darwin":
        try:
            # 맥에서 시스템 정보 명령어 실행
            result = subprocess.run(
                ["system_profiler", "SPCameraDataType"], capture_output=True, text=True
            )
            print("시스템 카메라 정보:", result.stdout)
        except Exception as e:
            print(f"시스템 카메라 정보 얻기 실패: {e}")

    # 테스트할 최대 카메라 인덱스
    max_index = 10

    for i in range(max_index):
        try:
            if system == "windows":
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)

            if cap.isOpened():
                # 카메라 이름 정보 얻기 (모든 시스템에서 작동하지 않을 수 있음)
                camera_name = ""
                try:
                    camera_name = (
                        cap.getBackendName() if hasattr(cap, "getBackendName") else ""
                    )
                except:
                    pass

                # 해상도 정보 얻기
                width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

                # 테스트 프레임 캡처
                ret, frame = cap.read()

                camera_info = {
                    "index": i,
                    "name": camera_name,
                    "resolution": f"{int(width)}x{int(height)}",
                    "capture_success": ret,
                }

                # 이미지 캡처에 성공한 경우에만 추가
                if ret:
                    print(f"카메라 인덱스 {i}: 사용 가능 ({camera_info['resolution']})")
                    available_cameras.append(camera_info)
                else:
                    print(f"카메라 인덱스 {i}: 응답하지만 이미지를 가져올 수 없음")

                cap.release()
            else:
                print(f"카메라 인덱스 {i}: 사용 불가")

        except Exception as e:
            print(f"카메라 인덱스 {i} 테스트 중 오류: {e}")

    print(f"사용 가능한 카메라: {len(available_cameras)}개")

    if not available_cameras:
        print("사용 가능한 카메라가 없습니다.")
        return None

    # 캡처 성공 여부와 해상도를 기준으로 정렬 (고해상도 우선)
    available_cameras.sort(
        key=lambda x: (
            x["capture_success"],
            int(x["resolution"].split("x")[0]) if "x" in x["resolution"] else 0,
        ),
        reverse=True,
    )

    # 인덱스만 추출
    return [camera["index"] for camera in available_cameras]


# 환경 변수에서 카메라 인덱스 설정을 가져옵니다 (없으면 기본값 사용)
def get_camera_index_from_env():
    system = platform.system().lower()
    if system == "darwin":  # macOS
        return os.environ.get("MAC_CAMERA_INDEX", CAMERA_CONFIG["darwin"]["index"])
    else:  # Windows 등 기타 OS
        return os.environ.get("WIN_CAMERA_INDEX", CAMERA_CONFIG["windows"]["index"])


def initialize_camera(index=None):
    """
    카메라 초기화 함수

    Args:
        index: 카메라 인덱스 (None이면 운영체제에 맞는 기본값 또는 자동 감지)

    Returns:
        초기화된 OpenCV VideoCapture 객체
    """
    system = platform.system().lower()

    # 카메라 구성 초기화 (첫 실행 시 한 번만)
    if CAMERA_CONFIG[system]["index"] is None:
        # 환경 변수에서 인덱스 설정 가져오기
        env_index = get_camera_index_from_env()
        if env_index is not None:
            CAMERA_CONFIG[system]["index"] = int(env_index)
            print(f"환경변수에서 카메라 인덱스 설정: {env_index}")
        else:
            # 자동으로 사용 가능한 웹캠 감지
            detected_cameras = detect_webcam()
            if detected_cameras:
                CAMERA_CONFIG[system]["index"] = detected_cameras[0]
                print(f"자동으로 카메라 인덱스 설정: {detected_cameras[0]}")
            else:
                # 기본값으로 설정
                CAMERA_CONFIG[system]["index"] = 0
                print("카메라를 감지할 수 없어 기본 인덱스 0으로 설정")

    # 명시적으로 인덱스가 제공된 경우 해당 인덱스 사용
    use_index = index if index is not None else CAMERA_CONFIG[system]["index"]

    print(f"운영체제: {system}, 카메라 인덱스: {use_index}")

    if system == "windows":
        # Windows에서는 DirectShow 사용
        cap = cv2.VideoCapture(
            use_index,
            cv2.CAP_DSHOW if CAMERA_CONFIG["windows"]["use_dshow"] else cv2.CAP_ANY,
        )
    else:
        # macOS나 기타 OS
        cap = cv2.VideoCapture(use_index)

    if not cap.isOpened():
        # 첫 번째 시도가 실패하면 다른 인덱스도 시도
        print(f"카메라 인덱스 {use_index} 열기 실패, 다른 인덱스 시도...")

        # 먼저 자동 감지된 카메라 목록에서 시도
        detected_cameras = detect_webcam()

        # 감지된 다른 카메라 시도
        if detected_cameras:
            for cam_idx in detected_cameras:
                if cam_idx != use_index:
                    print(f"카메라 인덱스 {cam_idx} 시도 중...")
                    if system == "windows":
                        cap = cv2.VideoCapture(
                            cam_idx,
                            (
                                cv2.CAP_DSHOW
                                if CAMERA_CONFIG["windows"]["use_dshow"]
                                else cv2.CAP_ANY
                            ),
                        )
                    else:
                        cap = cv2.VideoCapture(cam_idx)

                    if cap.isOpened():
                        print(f"카메라 인덱스 {cam_idx}로 성공적으로 연결")
                        # 성공한 인덱스를 기록
                        CAMERA_CONFIG[system]["index"] = cam_idx
                        break

        # 감지된 카메라도 실패하면 기본 인덱스 순서대로 시도
        if not cap.isOpened():
            backup_indexes = [0, 1, 2]
            for backup_idx in backup_indexes:
                if backup_idx != use_index and (
                    not detected_cameras or backup_idx not in detected_cameras
                ):
                    print(f"기본 카메라 인덱스 {backup_idx} 시도 중...")
                    if system == "windows":
                        cap = cv2.VideoCapture(
                            backup_idx,
                            (
                                cv2.CAP_DSHOW
                                if CAMERA_CONFIG["windows"]["use_dshow"]
                                else cv2.CAP_ANY
                            ),
                        )
                    else:
                        cap = cv2.VideoCapture(backup_idx)

                    if cap.isOpened():
                        print(f"카메라 인덱스 {backup_idx}로 성공적으로 연결")
                        # 성공한 인덱스를 기록
                        CAMERA_CONFIG[system]["index"] = backup_idx
                        break

    if not cap.isOpened():
        raise RuntimeError(
            f"어떤 카메라도 열 수 없습니다. 카메라 연결 상태를 확인하세요."
        )

    # 카메라 설정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print(f"카메라(index={CAMERA_CONFIG[system]['index']}) 초기화 완료")
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

            # 현재 운영체제에 맞는 인덱스로 다시 열기
            system = platform.system().lower()
            index = CAMERA_CONFIG[system]["index"]

            if system == "windows":
                cap.open(
                    index,
                    (
                        cv2.CAP_DSHOW
                        if CAMERA_CONFIG["windows"]["use_dshow"]
                        else cv2.CAP_ANY
                    ),
                )
            else:
                cap.open(index)

            time.sleep(retry_delay)

        success, frame = cap.read()

        if success and frame is not None:
            return frame

        retry_count += 1
        print(f"프레임 읽기 실패. 재시도 중... ({retry_count}/{max_retries})")
        time.sleep(retry_delay)

    # 모든 재시도 실패 시
    raise RuntimeError(
        "카메라로부터 프레임을 읽을 수 없습니다. 카메라 연결 상태를 확인하세요."
    )
