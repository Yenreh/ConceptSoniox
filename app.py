#!/usr/bin/env python3
"""
Aplicación Flask para transcripción de audio en vivo
Usa Soniox Speech-to-Text API con WebSockets
"""

import os
import base64
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

from controller_soniox import soniox_controller
from controller_deepgram import deepgram_controller

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Deepgram streaming STT via WebSocket (Flask-SocketIO)
@socketio.on('deepgram_streaming_stt')
def handle_deepgram_streaming_stt(data):
    sid = request.sid
    url = data.get('url')
    try:
        deepgram_controller.start_streaming(sid, url, socketio)
    except ValueError as e:
        emit('deepgram_streaming_result', {'error': str(e)})
    except Exception as e:
        emit('deepgram_streaming_result', {'error': str(e)})

@socketio.on('deepgram_streaming_stop')
def handle_deepgram_streaming_stop():
    deepgram_controller.stop_streaming(request.sid)

@app.route('/')
def index():
    """Página principal con interfaz de transcripción en vivo"""
    return render_template('index.html')

# --- DEEPGRAM API ENDPOINTS ---

@app.route('/deepgram/local-stt', methods=['POST'])
def deepgram_local_stt():
    file = request.files.get('audio')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    try:
        result = deepgram_controller.transcribe_local_upload(file)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/deepgram/remote-stt', methods=['POST'])
def deepgram_remote_stt():
    data = request.get_json()
    url = data.get('url') if data else None
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    try:
        result = deepgram_controller.transcribe_remote_url(url)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/deepgram/tts', methods=['POST'])
def deepgram_tts():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No request data provided'}), 400
    text = data.get('text')
    model = data.get('model')
    encoding = data.get('encoding')
    sample_rate = data.get('sample_rate')
    mip_opt_out = data.get('mip_opt_out', 'false')
    try:
        audio_b64 = deepgram_controller.synthesize_speech(
            text=text,
            model=model,
            encoding=encoding,
            sample_rate=sample_rate,
            mip_opt_out=mip_opt_out,
        )
        return jsonify({'audio': audio_b64})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Endpoint de salud"""
    return jsonify({'status': 'ok'})

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
        audio_b64 = data.get('audio')
        if not audio_b64:
            raise ValueError('No audio payload received')
        audio_data = base64.b64decode(audio_b64)
        audio_format = data.get('format', 'wav')
        model = data.get('model')
        result = soniox_controller.transcribe_streaming_chunk(audio_data, audio_format=audio_format, model=model)

        if result.get('text'):
            payload = {
                'text': result['text'],
                'is_final': True,
                'timestamp': data.get('timestamp', 0),
                'model': result.get('model'),
            }
            if result.get('confidence') is not None:
                payload['confidence'] = result['confidence']
            emit('transcription', payload)
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
        audio_b64 = data.get('audio')
        if not audio_b64:
            raise ValueError('No audio payload received')
        audio_data = base64.b64decode(audio_b64)
        
        # Detectar formato del archivo
        file_format = data.get('format', 'mp3')
        model = data.get('model')
        result = soniox_controller.transcribe_file_audio(audio_data, file_format=file_format, model=model)

        emit('file_transcription', {
            'text': result['text'],
            'words': result['words'],
            'confidence': result.get('confidence'),
            'format': result.get('format'),
            'model': result.get('model'),
        })
    except Exception as e:
        print(f"Error al transcribir archivo: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("=" * 50)
    print("Servidor de Transcripción en Vivo")
    print("=" * 50)
    print(f"URL: http://localhost:5000")
    print("=" * 50)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
