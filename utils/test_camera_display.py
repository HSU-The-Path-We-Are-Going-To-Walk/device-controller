import cv2
import time
import platform
import argparse


def test_camera_display(index=None):
    """
    지정된 인덱스의 카메라 영상을 표시하여 어떤 카메라가 사용되는지 확인합니다.

    Args:
        index: 테스트할 카메라 인덱스 (None이면 0, 1 모두 테스트)
    """
    system = platform.system().lower()
    print(f"운영체제: {system}")

    # 테스트할 인덱스 목록
    indexes = [0, 1] if index is None else [index]

    for idx in indexes:
        print(f"\n카메라 인덱스 {idx} 테스트 중...")

        # 카메라 열기
        if system == "windows":
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        else:
            cap = cv2.VideoCapture(idx)

        if not cap.isOpened():
            print(f"카메라 인덱스 {idx}를 열 수 없습니다!")
            continue

        # 카메라 정보 출력
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"카메라 {idx} 해상도: {width}x{height}")

        # 이미지 캡처 및 표시
        print(f"카메라 {idx} 영상을 표시합니다. (3초간)")
        print("창을 닫으려면 'q' 키를 누르세요.")

        start_time = time.time()
        window_name = f"Camera {idx} Test"

        while time.time() - start_time < 3:  # 3초 동안 표시
            ret, frame = cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다!")
                break

            # 텍스트 표시
            text = f"Camera Index: {idx}"
            cv2.putText(
                frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
            )

            # 화면에 표시
            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # 자원 해제
        cap.release()
        cv2.destroyWindow(window_name)

    cv2.destroyAllWindows()
    print("\n테스트 완료!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="카메라 인덱스 테스트 프로그램")
    parser.add_argument("-i", "--index", type=int, help="테스트할 카메라 인덱스")
    args = parser.parse_args()

    test_camera_display(args.index)
