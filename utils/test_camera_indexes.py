import cv2

def test_camera_indexes():
    print("카메라 인덱스 테스트를 시작합니다...")
    for i in range(10):  # 0부터 9까지 인덱스 테스트
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"카메라 인덱스 {i} 사용 가능")
            ret, frame = cap.read()
            if ret:
                print(f"  - 이미지 캡처 성공 (인덱스 {i})")
                cv2.imwrite(f'camera_test_{i}.jpg', frame)
                print(f"  - 이미지가 camera_test_{i}.jpg로 저장되었습니다.")
            else:
                print(f"  - 이미지를 캡처할 수 없습니다 (인덱스 {i})")
            cap.release()
        else:
            print(f"카메라 인덱스 {i} 사용 불가")

if __name__ == "__main__":
    test_camera_indexes()
