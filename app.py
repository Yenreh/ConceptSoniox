#!/usr/bin/env python3
"""
Aplicación Flask para transcripción de audio en vivo
Usa Soniox Speech-to-Text API con WebSockets
"""

import os
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from soniox.speech_service import SpeechClient
from soniox.transcribe_file import transcribe_bytes_short
import base64

# Deepgram utils
from deepgram_utils import transcribe_local_audio, transcribe_remote_audio, text_to_speech
from deepgram_streaming import deepgram_streaming_stt
import threading
import queue
import json as pyjson
import websocket
import requests

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Cliente de Soniox
API_KEY = os.getenv('SONIOX_API_KEY')


# Deepgram streaming STT via WebSocket (Flask-SocketIO)

# Deepgram streaming control

# Store both thread and stop_flag for each session
deepgram_streaming_threads = {}  # sid: {'thread': t, 'stop_flag': stop_flag}

@socketio.on('deepgram_streaming_stt')
def handle_deepgram_streaming_stt(data):
    url = data.get('url')
    sid = request.sid
    if not url:
        emit('deepgram_streaming_result', {'error': 'No URL provided'})
        return
    stop_flag = threading.Event()
    def ws_thread():
        api_key = os.getenv("DEEPGRAM_API_KEY")
        ws_url = "wss://api.deepgram.com/v1/listen"
        ws_ref = {'ws': None}
        def on_open(ws):
            ws_ref['ws'] = ws
            def stream_audio():
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=4096):
                        if stop_flag.is_set():
                            ws.close()
                            break
                        ws.send(chunk, opcode=websocket.ABNF.OPCODE_BINARY)
                ws.close()
            threading.Thread(target=stream_audio, daemon=True).start()
        def on_message(ws, message):
            try:
                response = pyjson.loads(message)
                if response.get("type") == "Results":
                    transcript = response["channel"]["alternatives"][0].get("transcript", "")
                    if transcript:
                        socketio.emit('deepgram_streaming_result', {'transcript': transcript}, room=sid)
            except Exception:
                pass
        def on_close(ws, close_status_code, close_msg):
            socketio.emit('deepgram_streaming_result', {'done': True}, room=sid)
        def on_error(ws, error):
            socketio.emit('deepgram_streaming_result', {'error': str(error)}, room=sid)
        ws_app = websocket.WebSocketApp(
            ws_url,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            on_error=on_error,
            header=[f"Authorization: Token {api_key}"]
        )
        ws_ref['ws_app'] = ws_app
        ws_app.run_forever()
    t = threading.Thread(target=ws_thread, daemon=True)
    deepgram_streaming_threads[sid] = {'thread': t, 'stop_flag': stop_flag}
    t.start()

@socketio.on('deepgram_streaming_stop')
def handle_deepgram_streaming_stop():
    sid = request.sid
    entry = deepgram_streaming_threads.get(sid)
    if entry:
        stop_flag = entry.get('stop_flag')
        if stop_flag:
            stop_flag.set()
        deepgram_streaming_threads.pop(sid, None)

@app.route('/')
def index():
    """Página principal con interfaz de transcripción en vivo"""
    return render_template('index.html')

# --- DEEPGRAM API ENDPOINTS ---
import tempfile

@app.route('/deepgram/local-stt', methods=['POST'])
def deepgram_local_stt():
    file = request.files.get('audio')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    # Use a cross-platform temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[-1]) as tmp:
        file_path = tmp.name
        file.save(file_path)
    try:
        result = transcribe_local_audio(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.route('/deepgram/remote-stt', methods=['POST'])
def deepgram_remote_stt():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        result = transcribe_remote_audio(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/deepgram/tts', methods=['POST'])
def deepgram_tts():
    import tempfile
    data = request.get_json()
    text = data.get('text')
    model = data.get('model')
    encoding = data.get('encoding')
    sample_rate = data.get('sample_rate')
    mip_opt_out = data.get('mip_opt_out', 'false')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
        output_file = tmp.name
    try:
        text_to_speech(text, model, output_file, encoding, sample_rate, mip_opt_out)
        with open(output_file, 'rb') as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        return jsonify({'audio': audio_b64})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)

@app.route('/health')
def health():
    """Endpoint de salud"""
    return jsonify({'status': 'ok', 'api_configured': bool(API_KEY)})

@socketio.on('connect')
def handle_connect():
    """Maneja la conexión del cliente"""
    print('Cliente conectado')
    emit('status', {'message': 'Conectado al servidor', 'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Maneja la desconexión del cliente"""
    print('Cliente desconectado')

@socketio.on('start_recording')
def handle_start_recording():
    """Inicia la grabación"""
    print('Iniciando grabación...')
    emit('status', {'message': 'Grabación iniciada', 'status': 'recording'})

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """
    Maneja chunks de audio en tiempo real
    El audio viene en formato WAV desde el navegador (ya convertido en JS)
    """
    try:
        # Decodificar el audio base64
        audio_data = base64.b64decode(data['audio'])
        
        # Transcribir el chunk de audio (ya viene en WAV desde el navegador)
        with SpeechClient(api_key=API_KEY) as client:
            result = transcribe_bytes_short(
                audio_data,
                client,
                model="es_v2",  # Español
                audio_format="wav",
            )
            
            # Extraer el texto
            if result.words:
                transcript = " ".join([word.text for word in result.words])
                
                # Enviar transcripción al cliente
                emit('transcription', {
                    'text': transcript,
                    'is_final': True,
                    'timestamp': data.get('timestamp', 0)
                })
    
    except Exception as e:
        print(f"Error al transcribir: {e}")
        emit('error', {'message': str(e)})

@socketio.on('stop_recording')
def handle_stop_recording():
    """Detiene la grabación"""
    print('Deteniendo grabación...')
    emit('status', {'message': 'Grabación detenida', 'status': 'stopped'})

@socketio.on('transcribe_file')
def handle_transcribe_file(data):
    """
    Transcribe un archivo de audio completo
    """
    try:
        # Decodificar el audio base64
        audio_data = base64.b64decode(data['audio'])
        
        # Detectar formato del archivo
        file_format = data.get('format', 'mp3')
        
        # Formatos soportados por Soniox
        supported_formats = ['aac', 'aiff', 'amr', 'asf', 'flac', 'mp3', 'ogg', 'wav']
        
        if file_format not in supported_formats:
            file_format = 'mp3'  # Default
        
        # Transcribir
        with SpeechClient(api_key=API_KEY) as client:
            result = transcribe_bytes_short(
                audio_data,
                client,
                model="es_v2",
                audio_format=file_format,
            )
            
            # Extraer texto y palabras con timestamps
            transcript = " ".join([word.text for word in result.words])
            
            words_with_timestamps = [
                {
                    'text': word.text,
                    'start_ms': word.start_ms,
                    'duration_ms': word.duration_ms
                }
                for word in result.words
            ]
            
            emit('file_transcription', {
                'text': transcript,
                'words': words_with_timestamps
            })
    
    except Exception as e:
        print(f"Error al transcribir archivo: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    if not API_KEY:
        print("ERROR: No se ha configurado SONIOX_API_KEY")
        print("Por favor, configura tu API key en el archivo .env")
        exit(1)
    
    print("=" * 50)
    print("Servidor de Transcripción en Vivo")
    print("=" * 50)
    print(f"URL: http://localhost:5000")
    print(f"Modelo: es_v2 (Español)")
    print("=" * 50)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
