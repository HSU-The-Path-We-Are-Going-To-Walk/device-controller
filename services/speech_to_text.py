import speech_recognition as sr
import tempfile
import os
from pydub import AudioSegment
import io
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def audio_to_text(audio_data, format="wav", language="ko-KR"):
    """
    바이너리 오디오 데이터를 받아 텍스트로 변환합니다.

    Args:
        audio_data (bytes): 오디오 바이너리 데이터
        format (str): 오디오 파일 형식 (wav, mp3 등)
        language (str): 인식할 언어 코드 (기본값: 한국어 'ko-KR')

    Returns:
        str: 텍스트로 변환된 음성 내용
    """
    try:
        # 임시 파일로 변환
        with tempfile.NamedTemporaryFile(
            suffix=f".{format}", delete=False
        ) as temp_audio:
            temp_audio.write(audio_data)
            temp_audio_path = temp_audio.name

        # 음성 인식기 초기화
        recognizer = sr.Recognizer()

        # 오디오 파일 로드
        logger.info("오디오 파일 로드 중...")
        with sr.AudioFile(temp_audio_path) as source:
            audio = recognizer.record(source)  # 전체 오디오 파일 읽기

        # 음성을 텍스트로 변환 (Google Speech Recognition 사용)
        logger.info("음성을 텍스트로 변환 중...")
        text = recognizer.recognize_google(audio, language=language)
        logger.info(f"변환된 텍스트: {text}")

        # 임시 파일 삭제
        os.unlink(temp_audio_path)

        return text.strip()

    except sr.UnknownValueError:
        logger.warning("음성을 인식할 수 없습니다.")
        # 임시 파일이 아직 남아있다면 삭제
        if "temp_audio_path" in locals() and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        return ""

    except sr.RequestError as e:
        logger.error(f"Google Speech Recognition 서비스에 접근할 수 없습니다; {e}")
        # 임시 파일이 아직 남아있다면 삭제
        if "temp_audio_path" in locals() and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        raise Exception(f"Speech Recognition 서비스 오류: {e}")

    except Exception as e:
        logger.error(f"STT 처리 중 오류 발생: {str(e)}")
        # 임시 파일이 아직 남아있다면 삭제
        if "temp_audio_path" in locals() and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        raise e


def webm_to_wav(webm_data):
    """
    WebM 형식의 오디오 데이터를 WAV 형식으로 변환합니다.

    Args:
        webm_data (bytes): WebM 오디오 바이너리 데이터

    Returns:
        bytes: WAV 형식의 오디오 바이너리 데이터
    """
    try:
        # 바이너리 데이터를 AudioSegment로 변환
        audio = AudioSegment.from_file(io.BytesIO(webm_data), format="webm")

        # WAV 형식으로 변환
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        return wav_io.getvalue()

    except Exception as e:
        logger.error(f"오디오 변환 중 오류 발생: {str(e)}")
        raise e
