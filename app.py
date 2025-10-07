#!/usr/bin/env python3
"""
Aplicación Flask para transcripción de audio en vivo
Usa Soniox Speech-to-Text API con WebSockets
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from soniox.speech_service import SpeechClient
from soniox.transcribe_file import transcribe_bytes_short
import base64

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*")

# Cliente de Soniox
API_KEY = os.getenv('SONIOX_API_KEY')

@app.route('/')
def index():
    """Página principal con interfaz de transcripción en vivo"""
    return render_template('index.html')

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
