import os
import websocket
import json
import requests
from dotenv import load_dotenv

def deepgram_streaming_stt(audio_url):
    """
    Streams audio from a remote URL to Deepgram's streaming API and returns the transcript.
    """
    load_dotenv()
    api_key = os.getenv("DEEPGRAM_API_KEY")
    ws_url = "wss://api.deepgram.com/v1/listen"
    headers = {"Authorization": f"Token {api_key}"}
    transcript = []
    
    def on_message(ws, message):
        try:
            response = json.loads(message)
            if response.get("type") == "Results":
                alt = response["channel"]["alternatives"][0]
                t = alt.get("transcript", "")
                if t:
                    transcript.append(t)
        except Exception:
            pass
    def on_error(ws, error):
        transcript.append(f"[ERROR] {error}")
    def on_close(ws, code, msg):
        pass
    def on_open(ws):
        def run():
            resp = requests.get(audio_url, stream=True)
            if resp.status_code == 200:
                for chunk in resp.iter_content(chunk_size=4096):
                    ws.send(chunk, opcode=websocket.ABNF.OPCODE_BINARY)
            ws.close()
        import threading
        threading.Thread(target=run).start()
    ws = websocket.WebSocketApp(ws_url, header=[f"Authorization: Token {api_key}"],
                                on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()
    return " ".join(transcript)
