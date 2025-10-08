import base64
import os
import threading
import tempfile
from typing import Any, Dict, Optional
from io import BytesIO

import requests
from deepgram import DeepgramClient
from deepgram.core.events import EventType
from deepgram.extensions.types.sockets import ListenV1SocketClientResponse
from dotenv import load_dotenv
from flask_socketio import SocketIO

load_dotenv()


class DeepgramController:
    """Centralizes Deepgram API interactions using the official Deepgram SDK."""

    def __init__(self, *, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self._api_key:
            raise RuntimeError("DEEPGRAM_API_KEY not configured. Check your .env file.")
        self._client = DeepgramClient(api_key=self._api_key)
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

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

    def start_streaming(self, sid: str, url: str, socketio: SocketIO) -> None:
        if not url:
            raise ValueError("No URL provided")

        stop_flag = threading.Event()

        def ws_thread() -> None:
            try:
                with self._client.listen.v1.connect(model="nova-3") as connection:
                    def on_open(_) -> None:
                        print("Connection opened")

                    def on_message(message: ListenV1SocketClientResponse) -> None:
                        if hasattr(message, 'channel'):
                            transcript = message.channel.alternatives[0].transcript if message.channel.alternatives else ""
                            if transcript:
                                socketio.emit("deepgram_streaming_result", {"transcript": transcript}, room=sid)

                    def on_close(_) -> None:
                        print("Connection closed")
                        socketio.emit("deepgram_streaming_result", {"done": True}, room=sid)

                    def on_error(error) -> None:
                        print(f"Error: {error}")
                        socketio.emit("deepgram_streaming_result", {"error": str(error)}, room=sid)

                    connection.on(EventType.OPEN, on_open)
                    connection.on(EventType.MESSAGE, on_message)
                    connection.on(EventType.CLOSE, on_close)
                    connection.on(EventType.ERROR, on_error)

                    # Start listening in background thread
                    listen_thread = threading.Thread(target=connection.start_listening, daemon=True)
                    listen_thread.start()

                    # Stream audio from URL
                    response = requests.get(url, stream=True, timeout=60)
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=4096):
                            if stop_flag.is_set():
                                break
                            if chunk:
                                from deepgram.extensions.types.sockets import ListenV1MediaMessage
                                connection.send_media(ListenV1MediaMessage(data=chunk))

                    # Finalize transcription
                    from deepgram.extensions.types.sockets import ListenV1ControlMessage
                    connection.send_control(ListenV1ControlMessage(type="Finalize"))

            except Exception as e:
                print(f"Streaming error: {e}")
                socketio.emit("deepgram_streaming_result", {"error": str(e)}, room=sid)

        thread = threading.Thread(target=ws_thread, daemon=True)
        with self._lock:
            self._sessions[sid] = {"thread": thread, "stop_flag": stop_flag}
        thread.start()

    def stop_streaming(self, sid: str) -> None:
        with self._lock:
            session = self._sessions.pop(sid, None)
        if not session:
            return
        stop_flag = session.get("stop_flag")
        if stop_flag:
            stop_flag.set()


deepgram_controller = DeepgramController()
