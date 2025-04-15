from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import logging
from services import speech_to_text
from typing import Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["audio"],
    responses={404: {"description": "Not found"}},
)


@router.post("/audio/speech-to-text")
async def convert_speech_to_text(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form("ko-KR"),
):
    """
    음성 파일을 받아 텍스트로 변환하는 엔드포인트

    Args:
        audio_file: 프론트엔드에서 전송한 오디오 파일 (WAV, MP3, WEBM 등)
        language: 인식할 언어 코드 (기본값: 한국어 'ko-KR')

    Returns:
        JSON 형태의 텍스트 변환 결과
    """
    try:
        logger.info(
            f"받은 오디오 파일: {audio_file.filename}, 콘텐츠 타입: {audio_file.content_type}"
        )

        # 오디오 파일 읽기
        contents = await audio_file.read()

        # 파일 형식 확인 및 처리
        format = audio_file.filename.split(".")[-1].lower()
        content_type = audio_file.content_type

        # WEBM 형식인 경우 WAV로 변환
        if "webm" in format or "webm" in content_type:
            logger.info("WebM 형식을 WAV로 변환 중...")
            contents = speech_to_text.webm_to_wav(contents)
            format = "wav"

        # 음성을 텍스트로 변환
        text = speech_to_text.audio_to_text(contents, format=format, language=language)
        logger.info(f"변환된 텍스트: {text}")

        return JSONResponse(content={"success": True, "text": text}, status_code=200)

    except Exception as e:
        logger.error(f"음성 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"음성 처리 중 오류가 발생했습니다: {str(e)}"
        )


# 추가: /speech-to-text 경로 (프론트엔드 요청에 맞춤)
@router.post("/speech-to-text")
async def root_speech_to_text(
    audio: UploadFile = File(...),  # 'audio' 필드 이름으로 변경
    language: Optional[str] = Form("ko-KR"),
):
    """
    프론트엔드 요청에 맞춘 음성 인식 엔드포인트

    Args:
        audio: 프론트엔드에서 전송한 오디오 파일 (WAV, MP3, WEBM 등) - 'audio' 필드로 전송
        language: 인식할 언어 코드 (기본값: 한국어 'ko-KR')

    Returns:
        JSON 형태의 텍스트 변환 결과
    """
    try:
        logger.info(
            f"받은 오디오 파일: {audio.filename}, 콘텐츠 타입: {audio.content_type}"
        )

        # 오디오 파일 읽기
        contents = await audio.read()

        # 파일 형식 확인 및 처리
        format = audio.filename.split(".")[-1].lower()
        content_type = audio.content_type

        # WEBM 형식인 경우 WAV로 변환
        if "webm" in format or "webm" in content_type:
            logger.info("WebM 형식을 WAV로 변환 중...")
            contents = speech_to_text.webm_to_wav(contents)
            format = "wav"

        # 음성을 텍스트로 변환
        text = speech_to_text.audio_to_text(contents, format=format, language=language)
        logger.info(f"변환된 텍스트: {text}")

        return JSONResponse(
            content={"text": text}, status_code=200  # 프론트엔드 예상 응답 형식에 맞춤
        )

    except Exception as e:
        logger.error(f"음성 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"음성 처리 중 오류가 발생했습니다: {str(e)}"
        )
