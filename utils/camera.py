import cv2
import time
import platform
import os
import subprocess
import re

# 설정 값을 저장할 딕셔너리
CAMERA_CONFIG = {
    "windows": {"index": None, "use_dshow": True},
    "darwin": {"index": None, "use_dshow": False},  # macOS는 'darwin'으로 표시됨
}

# 맥OS에서는 기본적으로 카메라 인덱스를 반전시킴 (0번이 USB, 1번이 내장)
# 환경변수가 명시적으로 false로 설정되었을 때만 반전 안함
REVERSE_CAMERA_INDEX_ON_MAC = (
    os.environ.get("REVERSE_CAMERA_INDEX_ON_MAC", "true").lower() != "false"
)

# 내장 웹캠 감지를 위한 키워드
BUILTIN_CAMERA_KEYWORDS = [
    "integrated",
    "내장",
    "built-in",
    "builtin",
    "internal",
    "laptop",
    "노트북",
    "notebook",
    "hd webcam",
    "realtek",
    "facetime",
    "전면",
]

# USB 웹캠 감지를 위한 키워드
USB_CAMERA_KEYWORDS = [
    "usb",
    "external",
    "외장",
    "logitech",
    "microsoft",
    "trust",
    "creative",
    "razer",
    "c920",
    "c922",
    "c270",
    "hd pro",
]

# 맥OS에서 카메라 반전 상태 출력
if platform.system().lower() == "darwin":
    print(f"맥OS 카메라 인덱스 반전 설정: {REVERSE_CAMERA_INDEX_ON_MAC}")


def get_camera_details_windows():
    """
    윈도우에서 연결된 모든 카메라 정보를 가져옵니다.
    """
    # 윈도우 환경이 아니면 빈 결과 반환
    if platform.system().lower() != "windows":
        return {}

    cameras = {}

    try:
        # WMI 모듈 사용 없이 Windows에서 카메라 감지
        # DirectShow를 통해 카메라 목록 얻기
        print("Windows에서 카메라 장치 정보 수집 시도...")

        # 기본 장치 정보 (인덱스별로)
        for i in range(10):  # 0-9 인덱스 검사
            try:
                camera_name = ""
                camera_desc = ""

                # DirectShow 사용하여 열기
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    # 장치 속성 가져오기 시도
                    try:
                        if hasattr(cap, "get"):
                            # DirectShow에서만 특정 속성을 지원할 수 있음
                            # 여기서는 가능한 정보만 수집
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            camera_desc = f"{width}x{height}"
                    except:
                        pass

                    # 텍스트 기반으로 장치 유형 추정
                    device_info = f"{camera_name} {camera_desc}"
                    is_builtin = any(
                        keyword.lower() in device_info.lower()
                        for keyword in BUILTIN_CAMERA_KEYWORDS
                    )
                    is_usb = any(
                        keyword.lower() in device_info.lower()
                        for keyword in USB_CAMERA_KEYWORDS
                    )

                    # 기본적으로 인덱스 0은 내장 웹캠으로 간주
                    if not is_builtin and not is_usb:
                        is_builtin = i == 0

                    # 장치 정보 저장
                    cameras[f"camera_{i}"] = {
                        "name": f"카메라 {i}",
                        "description": camera_desc,
                        "is_builtin": is_builtin,
                        "is_usb": is_usb or not is_builtin,  # 내장이 아니면 USB로 가정
                    }

                    print(
                        f"카메라 장치 감지: 인덱스 {i} - {'내장 웹캠' if is_builtin else 'USB 외장 웹캠' if is_usb else '알 수 없는 카메라'}"
                    )
                    cap.release()
            except Exception as e:
                print(f"카메라 인덱스 {i} 장치 정보 수집 오류: {e}")

        # 추가: Windows PowerShell 명령어로 장치 정보를 얻을 수도 있음
        # 이 부분은 Windows에서만 작동함

        return cameras

    except Exception as e:
        print(f"Windows 카메라 정보 수집 중 오류: {e}")
        return {}


def detect_webcam():
    """
    사용 가능한 웹캠을 감지하고 가장 적합한 인덱스를 반환합니다.

    Returns:
        웹캠으로 인식된 카메라 인덱스 목록 (외장 웹캠 우선, 내장 웹캠 후순위)
    """
    system = platform.system().lower()
    print(f"운영체제 {system}에서 사용 가능한 웹캠을 검색합니다...")

    # 사용 가능한 카메라 인덱스와 정보를 저장할 리스트
    available_cameras = []

    # Windows에서 디바이스 정보 먼저 수집
    system_cameras = {}
    if system == "windows":
        system_cameras = get_camera_details_windows()
        # 발견된 카메라 장치 정보 출력
        if system_cameras:
            print(f"{len(system_cameras)}개의 카메라 장치가 시스템에서 감지되었습니다.")

    # macOS에서 외부 명령어로 카메라 정보 얻기
    elif system == "darwin":
        try:
            # 맥에서 시스템 정보 명령어 실행
            result = subprocess.run(
                ["system_profiler", "SPCameraDataType"], capture_output=True, text=True
            )
            camera_info = result.stdout
            print("시스템 카메라 정보:", camera_info)
        except Exception as e:
            print(f"시스템 카메라 정보 얻기 실패: {e}")

    # 테스트할 최대 카메라 인덱스
    max_index = 10

    print("카메라 인덱스 감지를 시작합니다...")
    for i in range(max_index):
        try:
            if system == "windows":
                # Windows에서는 확실히 DirectShow 사용
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)

            if cap.isOpened():
                # 카메라 이름과 정보 얻기 시도
                camera_name = ""
                camera_desc = ""

                if system == "windows":
                    try:
                        # Windows에서는 추가 속성 얻기 시도
                        camera_name = (
                            cap.getBackendName()
                            if hasattr(cap, "getBackendName")
                            else ""
                        )
                        # DirectShow에서만 작동하는 속성
                        fourcc = cv2.CAP_PROP_FOURCC
                        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    except:
                        pass

                # 테스트 프레임 캡처
                ret, frame = cap.read()

                # 내장/외장 웹캠 여부 판단
                is_builtin = False
                is_usb = False

                # 윈도우에서 시스템 정보 기반으로 내장/외장 판단
                if system == "windows" and system_cameras:
                    # 해당 인덱스와 매칭되는 시스템 카메라 찾기
                    # (정확한 매핑은 어렵지만, 발견된 순서와 OpenCV 인덱스 간에 어느 정도 연관성이 있음)
                    for camera_id, details in system_cameras.items():
                        is_builtin = details.get("is_builtin", False)
                        is_usb = details.get("is_usb", False)
                        camera_desc = details.get("description", "")
                        camera_name = details.get("name", "")
                        # 이미 발견된 카메라에 대한 정보가 있다면 사용
                        if len(available_cameras) == i:
                            break

                # 이름이나 설명에서 내장/외장 여부 추정
                if not is_builtin and not is_usb:
                    camera_info = (camera_name + " " + camera_desc).lower()
                    is_builtin = any(
                        keyword in camera_info for keyword in BUILTIN_CAMERA_KEYWORDS
                    )
                    is_usb = any(
                        keyword in camera_info for keyword in USB_CAMERA_KEYWORDS
                    )

                    # 기본적으로, 이름에 내장/외장 키워드가 없다면 인덱스로 추정
                    if not is_builtin and not is_usb:
                        if system == "darwin" and REVERSE_CAMERA_INDEX_ON_MAC:
                            # 맥OS에서 인덱스 반전: 0번이 USB, 1번이 내장
                            is_builtin = i == 1
                            is_usb = i == 0
                        else:
                            # 일반적으로 0번 인덱스는 내장 웹캠인 경우가 많음
                            is_builtin = i == 0
                            is_usb = i > 0

                camera_info = {
                    "index": i,
                    "name": camera_name,
                    "description": camera_desc,
                    "resolution": f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
                    "capture_success": ret,
                    "is_builtin": is_builtin,
                    "is_usb": is_usb,
                }

                # 이미지 캡처에 성공한 경우에만 추가
                if ret:
                    device_type = (
                        "내장 웹캠"
                        if is_builtin
                        else "USB 외장 웹캠" if is_usb else "기타 카메라"
                    )
                    print(
                        f"카메라 인덱스 {i}: 사용 가능 ({camera_info['resolution']}) - {device_type} {camera_name} {camera_desc}"
                    )
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

    # 우선순위: 1. USB 외장 웹캠, 2. 기타 카메라, 3. 내장 웹캠
    # 각 카테고리 내에서는 고해상도 우선
    def get_camera_priority(camera):
        # 1순위: USB 외장 웹캠(3), 2순위: 기타 카메라(2), 3순위: 내장 웹캠(1)
        if camera["is_usb"]:
            type_priority = 3
        elif not camera["is_builtin"]:
            type_priority = 2
        else:
            type_priority = 1

        # 각 타입 내에서 해상도로 정렬
        width = 0
        height = 0
        if "x" in camera["resolution"]:
            try:
                width_str, height_str = camera["resolution"].split("x")
                width = int(width_str)
                height = int(height_str)
            except:
                pass

        # 정상적으로 캡처가 되는지가 가장 중요함
        return (camera["capture_success"], type_priority, width * height)

    # 카메라 우선순위에 따라 정렬 (USB 외장 웹캠 > 기타 > 내장 웹캠, 그리고 각 카테고리 내에서는 해상도 높은 순)
    available_cameras.sort(key=get_camera_priority, reverse=True)

    # 맥OS에서 카메라 인덱스 반전 옵션이 활성화된 경우
    if system == "darwin" and REVERSE_CAMERA_INDEX_ON_MAC:
        print("맥OS에서 카메라 인덱스 반전 옵션 활성화됨")

    # 정렬된 카메라 정보 출력
    print("\n카메라 우선순위 결과:")
    for i, cam in enumerate(available_cameras):
        device_type = (
            "내장 웹캠"
            if cam["is_builtin"]
            else "USB 외장 웹캠" if cam["is_usb"] else "기타 카메라"
        )
        print(f"{i+1}. 인덱스 {cam['index']} - {device_type} ({cam['resolution']})")

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
                print(
                    f"자동으로 카메라 인덱스 설정: {detected_cameras[0]} (외장 웹캠 우선)"
                )
            else:
                # 기본값으로 설정
                CAMERA_CONFIG[system]["index"] = 0
                print("카메라를 감지할 수 없어 기본 인덱스 0으로 설정")

    # 명시적으로 인덱스가 제공된 경우 해당 인덱스 사용
    use_index = index if index is not None else CAMERA_CONFIG[system]["index"]

    print(f"운영체제: {system}, 카메라 인덱스: {use_index}")

    if system == "windows":
        # Windows에서는 DirectShow 사용 (USB 웹캠 감지에 필수)
        cap = cv2.VideoCapture(use_index, cv2.CAP_DSHOW)
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
                        cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
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
                        cap = cv2.VideoCapture(backup_idx, cv2.CAP_DSHOW)
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
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

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
