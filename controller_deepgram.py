import base64
import os
import threading
import tempfile
from typing import Any, Dict, Optional

import requests
import websocket
from dotenv import load_dotenv
from flask_socketio import SocketIO

load_dotenv()


class DeepgramController:
    """Centralizes Deepgram API interactions (REST and streaming)."""

    _LISTEN_URL = "https://api.deepgram.com/v1/listen"
    _SPEAK_URL = "https://api.deepgram.com/v1/speak"
    _STREAM_URL = "wss://api.deepgram.com/v1/listen"

    def __init__(self, *, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self._api_key:
            raise RuntimeError("DEEPGRAM_API_KEY not configured. Check your .env file.")
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def _headers(self, content_type: Optional[str] = None) -> Dict[str, str]:
        headers = {"Authorization": f"Token {self._api_key}"}
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _listen_request(
        self,
        *,
        data: Optional[bytes] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        response = requests.post(
            self._LISTEN_URL,
            headers=self._headers(content_type or ("application/json" if json_payload else None)),
            data=data,
            json=json_payload,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def transcribe_local_upload(self, file_storage) -> Dict[str, Any]:
        if file_storage is None:
            raise ValueError("No file uploaded")
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_storage.filename)[-1]) as tmp:
            file_path = tmp.name
            file_storage.save(file_path)
        try:
            with open(file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            return self._listen_request(data=audio_data, content_type="audio/*")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    def transcribe_remote_url(self, url: Optional[str]) -> Dict[str, Any]:
        if not url:
            raise ValueError("No URL provided")
        return self._listen_request(json_payload={"url": url})

    def synthesize_speech(
        self,
        *,
        text: str,
        model: str,
        encoding: str,
        sample_rate: Any,
        mip_opt_out: str = "false",
    ) -> str:
        if not text:
            raise ValueError("No text provided")
        params = {
            "model": model,
            "encoding": encoding,
            "sample_rate": sample_rate,
        }
        if mip_opt_out == "true":
            params["mip_opt_out"] = "true"
        response = requests.post(
            self._SPEAK_URL,
            headers=self._headers("application/json"),
            params={k: v for k, v in params.items() if v is not None},
            json={"text": text},
            timeout=60,
        )
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

    def start_streaming(self, sid: str, url: str, socketio: SocketIO) -> None:
        if not url:
            raise ValueError("No URL provided")

        stop_flag = threading.Event()

        def ws_thread() -> None:
            def on_open(ws: websocket.WebSocketApp) -> None:
                def stream_audio() -> None:
                    response = requests.get(url, stream=True, timeout=60)
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=4096):
                            if stop_flag.is_set():
                                ws.close()
                                break
                            ws.send(chunk, opcode=websocket.ABNF.OPCODE_BINARY)
                    ws.close()

                threading.Thread(target=stream_audio, daemon=True).start()

            def on_message(ws: websocket.WebSocketApp, message: str) -> None:
                import json as pyjson

                try:
                    response = pyjson.loads(message)
                    if response.get("type") == "Results":
                        transcript = response["channel"]["alternatives"][0].get("transcript", "")
                        if transcript:
                            socketio.emit("deepgram_streaming_result", {"transcript": transcript}, room=sid)
                except Exception:
                    pass

            def on_close(ws: websocket.WebSocketApp, close_status_code: int, close_msg: str) -> None:
                socketio.emit("deepgram_streaming_result", {"done": True}, room=sid)

            def on_error(ws: websocket.WebSocketApp, error: Exception) -> None:
                socketio.emit("deepgram_streaming_result", {"error": str(error)}, room=sid)

            ws_app = websocket.WebSocketApp(
                self._STREAM_URL,
                on_open=on_open,
                on_message=on_message,
                on_close=on_close,
                on_error=on_error,
                header=[f"Authorization: Token {self._api_key}"],
            )
            ws_app.run_forever()

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
