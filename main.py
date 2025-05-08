from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import button, vision, audio
import uvicorn
import signal
import sys

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # 테스트 환경에서는 모든 오리진 허용 (프로덕션에서는 특정 오리진만 허용하는 것이 좋음)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(button.router)
# app.include_router(vision.router)
# app.include_router(audio.router)


# Ctrl+C 시그널 핸들러
def signal_handler(sig, frame):
    print("\n서버가 종료됩니다. 안전하게 종료 중...")
    sys.exit(0)


# SIGINT(Ctrl+C) 시그널에 핸들러 등록
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    try:
        print("서버가 시작되었습니다. 종료하려면 Ctrl+C를 누르세요.")
        # 기본 서버 설정으로 실행
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n서버가 종료됩니다. 안전하게 종료 중...")
        sys.exit(0)
