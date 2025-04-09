from fastapi import FastAPI, Request
from routers import button, vision
import uvicorn
import signal
import sys
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from typing import AsyncGenerator
import queue
import threading

app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # 모든 출처 허용 (실제 환경에서는 특정 출처만 허용하는 것이 좋음)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 사람 감지 상태 저장 변수
person_detected = False
# 세션 이벤트를 관리하는 글로벌 큐
session_events = queue.Queue()

app.include_router(button.router)
app.include_router(vision.router)


# 세션 초기화 엔드포인트 추가
@app.post("/sessionReset")
async def session_reset():
    global person_detected
    person_detected = False
    # 세션 리셋 이벤트를 큐에 추가
    session_events.put({"event": "reset"})
    return {"message": "Session has been reset"}


# 사람 감지 시작 엔드포인트 추가
@app.post("/sessionStart")
async def session_start():
    global person_detected
    person_detected = True
    return {"message": "Session has been started"}


# 세션 상태 확인 엔드포인트
@app.get("/sessionStatus")
async def session_status():
    global person_detected
    return {"reset": not person_detected}


# SSE 이벤트 스트림 생성 함수
async def event_generator() -> AsyncGenerator[str, None]:
    while True:
        # 큐에서 이벤트가 있는지 확인하지만 블로킹하지 않음
        try:
            event = session_events.get_nowait()
            yield f"data: {event}\n\n"
        except queue.Empty:
            pass  # 이벤트가 없으면 계속 진행

        # 클라이언트 연결 유지를 위한 주기적인 빈 메시지 전송
        yield f"data: {{'type': 'heartbeat'}}\n\n"
        await asyncio.sleep(5)  # 5초마다 하트비트 전송


# SSE 엔드포인트 추가
@app.get("/sessionEvents")
async def session_events_endpoint(request: Request):
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Nginx 프록시 버퍼링 비활성화
        },
    )


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
