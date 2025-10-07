#!/usr/bin/env python3
"""
Prueba de concepto simple para Soniox Speech-to-Text API
Transcribe audio a texto usando la API de Soniox
Soporta más de 60 idiomas con alta precisión
"""

import os
from dotenv import load_dotenv
from soniox.speech_service import SpeechClient
from soniox.transcribe_file import transcribe_file_short

def transcribe_audio(audio_file_path):
    """
    Transcribe un archivo de audio a texto
    
    Args:
        audio_file_path: Ruta al archivo de audio
    
    Returns:
        Transcripción del audio
    """
    load_dotenv()
    
    api_key = os.getenv('SONIOX_API_KEY')
    
    if not api_key:
        print("Error: Debes configurar SONIOX_API_KEY en el archivo .env")
        print("Obtén tu API key en: https://console.soniox.com/")
        return None
    
    print(f"Transcribiendo archivo: {audio_file_path}")
    print(f"Usando Soniox Speech-to-Text API (Legacy)")
    print(f"Modelo: es_v2 (Español optimizado)\n")
    
    try:
        # Crear cliente
        with SpeechClient(api_key=api_key) as client:
            # Transcribir el archivo directamente
            # transcribe_file_short toma el PATH del archivo, no los bytes
            result = transcribe_file_short(
                audio_file_path,
                client,
                model="es_v2",  # Modelo legacy para español
            )
            
            # Extraer el texto
            transcript = ""
            if result.words:
                transcript = " ".join([word.text for word in result.words])
            
            return transcript
            
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{audio_file_path}'")
        return None
    except Exception as e:
        print(f"Error al transcribir audio: {e}")
        print("\nVerifica que:")
        print("1. Tu API key sea correcta")
        print("2. Tengas conexión a internet")
        print("3. El archivo de audio sea válido")
        print("4. Tu cuenta tenga cuota disponible")
        import traceback
        traceback.print_exc()
        return None

def main():
    # Archivo de audio de ejemplo
    # Puedes usar archivos: mp3, wav, ogg, flac, webm, etc.
    audio_file = "sample_audio.mp3"
    
    # Si no existe un archivo de ejemplo, mostrar instrucciones
    if not os.path.exists(audio_file):
        print(f"No se encontró el archivo '{audio_file}'")
        print("\nColoca un archivo de audio en el directorio actual y actualiza el nombre.")
        print("Formatos soportados: mp3, wav, ogg, flac, aac, webm, amr, asf, aiff")
        print("\nEjemplo: python speech_to_text.py")
        return
    
    # Transcribir el audio
    result = transcribe_audio(audio_file)
    
    if result:
        print("\n" + "="*50)
        print("TRANSCRIPCIÓN:")
        print("="*50)
        print(result)
        print("="*50)
        
        # Guardar en archivo de texto
        output_file = "transcription.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n✓ Transcripción guardada en: {output_file}")
    else:
        print("\n✗ No se pudo transcribir el audio")

if __name__ == "__main__":
    main()
