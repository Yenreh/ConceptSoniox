import os
import statistics
from threading import Lock
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from soniox.speech_service import SpeechClient
from soniox.transcribe_file import transcribe_bytes_short

load_dotenv()

SUPPORTED_FORMATS = {
    "aac",
    "aiff",
    "amr",
    "asf",
    "flac",
    "mp3",
    "ogg",
    "wav",
}


class SonioxController:
    """Manages Soniox transcription workflows with shared client reuse."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
    ) -> None:
        self._api_key = api_key or os.getenv("SONIOX_API_KEY")
        if not self._api_key:
            raise RuntimeError("SONIOX_API_KEY not configured. Check your .env file.")
        self._default_model = default_model or os.getenv("SONIOX_MODEL", "es_v2")
        self._client: Optional[SpeechClient] = None
        self._lock = Lock()

    def _get_client(self) -> SpeechClient:
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self._client = SpeechClient(api_key=self._api_key)
        return self._client

    @staticmethod
    def _format_words(words: List[Any]) -> List[Dict[str, Any]]:
        formatted: List[Dict[str, Any]] = []
        for word in words:
            formatted.append(
                {
                    "text": word.text,
                    "start_ms": word.start_ms,
                    "end_ms": word.start_ms + word.duration_ms,
                    "duration_ms": word.duration_ms,
                    "confidence": getattr(word, "confidence", None),
                }
            )
        return formatted

    @staticmethod
    def _extract_transcript(words: List[Any]) -> str:
        return " ".join(word.text for word in words) if words else ""

    @staticmethod
    def _confidence(words: List[Any]) -> Optional[float]:
        confidences = [word.confidence for word in words if getattr(word, "confidence", None) is not None]
        if not confidences:
            return None
        return statistics.fmean(confidences)

    @staticmethod
    def _normalise_format(file_format: str) -> str:
        fmt = (file_format or "mp3").lower()
        if fmt not in SUPPORTED_FORMATS:
            return "mp3"
        return fmt

    def transcribe_streaming_chunk(
        self,
        audio_bytes: bytes,
        *,
        model: Optional[str] = None,
        audio_format: str = "wav",
    ) -> Dict[str, Any]:
        client = self._get_client()
        result = transcribe_bytes_short(
            audio_bytes,
            client,
            model=model or self._default_model,
            audio_format=audio_format,
        )

        words = getattr(result, "words", []) or []
        transcript = self._extract_transcript(words)

        return {
            "text": transcript,
            "words": self._format_words(words),
            "confidence": self._confidence(words),
            "model": model or self._default_model,
        }

    def transcribe_file_audio(
        self,
        audio_bytes: bytes,
        *,
        file_format: str = "mp3",
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        client = self._get_client()
        fmt = self._normalise_format(file_format)
        result = transcribe_bytes_short(
            audio_bytes,
            client,
            model=model or self._default_model,
            audio_format=fmt,
        )

        words = getattr(result, "words", []) or []

        return {
            "text": self._extract_transcript(words),
            "words": self._format_words(words),
            "confidence": self._confidence(words),
            "model": model or self._default_model,
            "format": fmt,
        }

    def shutdown(self) -> None:
        if self._client is not None:
            with self._lock:
                if self._client is not None:
                    self._client.close()
                    self._client = None


soniox_controller = SonioxController()
