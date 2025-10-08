import base64
import os
import tempfile
from typing import Any, Dict, Optional
from io import BytesIO

from deepgram import DeepgramClient
from dotenv import load_dotenv

load_dotenv()


class DeepgramController:
    """Centralizes Deepgram API interactions using the official Deepgram SDK."""

    def __init__(self, *, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self._api_key:
            raise RuntimeError("DEEPGRAM_API_KEY not configured. Check your .env file.")
        self._client = DeepgramClient(api_key=self._api_key)

    def transcribe_local_upload(self, file_storage, language: str = "es") -> Dict[str, Any]:
        """Transcribe uploaded audio file using Deepgram SDK."""
        if file_storage is None:
            raise ValueError("No file uploaded")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_storage.filename)[-1]) as tmp:
            file_path = tmp.name
            file_storage.save(file_path)
        
        try:
            with open(file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Debug: Check audio file size
            audio_size = len(audio_data)
            
            if audio_size == 0:
                raise ValueError("Audio file is empty")
            
            # Use Deepgram SDK for transcription with additional parameters
            response = self._client.listen.v1.media.transcribe_file(
                request=audio_data,
                model="nova-3",
                smart_format=True,
                punctuate=True,
                diarize=False,
                language=language  # Ahora es configurable
            )

            
            # Convert SDK response to dict format expected by the app
            return {
                "metadata": {
                    "request_id": response.metadata.request_id if response.metadata else None,
                    "model_info": response.metadata.model_info if response.metadata else None,
                    "duration": response.metadata.duration if response.metadata else None,
                },
                "results": {
                    "channels": [
                        {
                            "alternatives": [
                                {
                                    "transcript": alt.transcript,
                                    "confidence": alt.confidence,
                                    "words": [
                                        {
                                            "word": word.word,
                                            "start": word.start,
                                            "end": word.end,
                                            "confidence": word.confidence,
                                        }
                                        for word in (alt.words or [])
                                    ] if alt.words else []
                                }
                                for alt in (channel.alternatives or [])
                            ]
                        }
                        for channel in (response.results.channels or [])
                    ] if response.results and response.results.channels else []
                }
            }
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def transcribe_remote_url(self, url: str, language: str = "es") -> Dict[str, Any]:
        """Transcribe audio from a remote URL using Deepgram SDK."""
        if not url:
            raise ValueError("No URL provided")
        
        print(f"DEBUG: Transcribing URL: {url}")
        
        # Use Deepgram SDK for URL transcription
        response = self._client.listen.v1.media.transcribe_url(
            url=url,
            model="nova-3",
            smart_format=True,
            punctuate=True,
            diarize=False,
            language=language  # Ahora es configurable
        )
        
        # Debug: Print response structure
        print(f"DEBUG: Response metadata: {response.metadata}")
        if response.results and response.results.channels:
            print(f"DEBUG: Number of channels: {len(response.results.channels)}")
            if response.results.channels[0].alternatives:
                transcript = response.results.channels[0].alternatives[0].transcript
                print(f"DEBUG: First transcript: '{transcript}'")
                print(f"DEBUG: Transcript length: {len(transcript)} chars")
        
        # Convert SDK response to dict format expected by the app
        return {
            "metadata": {
                "request_id": response.metadata.request_id if response.metadata else None,
                "model_info": response.metadata.model_info if response.metadata else None,
                "duration": response.metadata.duration if response.metadata else None,
            },
            "results": {
                "channels": [
                    {
                        "alternatives": [
                            {
                                "transcript": alt.transcript,
                                "confidence": alt.confidence,
                                "words": [
                                    {
                                        "word": word.word,
                                        "start": word.start,
                                        "end": word.end,
                                        "confidence": word.confidence,
                                    }
                                    for word in (alt.words or [])
                                ] if alt.words else []
                            }
                            for alt in (channel.alternatives or [])
                        ]
                    }
                    for channel in (response.results.channels or [])
                ] if response.results and response.results.channels else []
            }
        }

    def transcribe_microphone_chunk(
        self,
        audio_data: bytes,
        audio_format: str = "wav",
        language: str = "es"
    ) -> Dict[str, Any]:
        """Transcribe audio chunk from microphone using Deepgram SDK."""
        if not audio_data:
            raise ValueError("No audio data provided")
        
        # Use Deepgram SDK for transcription
        response = self._client.listen.v1.media.transcribe_file(
            request=audio_data,
            model="nova-3",
            smart_format=True,
            punctuate=True,
            language=language
        )
        
        # Extract transcript from response
        transcript = ""
        confidence = 0.0
        
        if response.results and response.results.channels:
            if response.results.channels[0].alternatives:
                alt = response.results.channels[0].alternatives[0]
                transcript = alt.transcript or ""
                confidence = alt.confidence or 0.0
        
        return {
            "text": transcript,
            "confidence": confidence,
            "format": audio_format,
            "model": "nova-3"
        }

    def synthesize_speech(
        self,
        *,
        text: str,
        model: str,
        encoding: str,
        sample_rate: Any,
        mip_opt_out: str = "false",
    ) -> str:
        """Synthesize speech using Deepgram SDK."""
        if not text:
            raise ValueError("No text provided")
        
        # Use Deepgram SDK for TTS
        audio_stream = self._client.speak.v1.audio.generate(
            text=text,
            model=model,
            encoding=encoding,
            sample_rate=int(sample_rate) if sample_rate else None,
            mip_opt_out=(mip_opt_out == "true")
        )
        
        # Collect all audio chunks
        audio_buffer = BytesIO()
        for chunk in audio_stream:
            audio_buffer.write(chunk)
        
        # Return base64 encoded audio
        audio_buffer.seek(0)
        return base64.b64encode(audio_buffer.read()).decode("utf-8")


deepgram_controller = DeepgramController()
