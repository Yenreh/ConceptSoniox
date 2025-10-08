# Concept Proof · Soniox + Deepgram

Prueba de concepto que combina transcripción y síntesis de voz usando Soniox y Deepgram sobre una app Flask con WebSockets.

## Qué incluye

- **Interfaz web**
  - Pestaña Soniox: transcripción en vivo desde el navegador, subida de archivos y métricas de palabras/caracteres.
  - Pestaña Deepgram: transcripción en vivo multilenguaje, carga de archivos locales, URLs remotas y texto a voz.
- **Script CLI** (`speech_to_text.py`) para transcribir archivos con Soniox y guardar el resultado en `transcription.txt`.

## Requisitos rápidos

- Python 3.10 o superior
- Cuenta en Soniox (clave `SONIOX_API_KEY`)
- Cuenta en Deepgram (clave `DEEPGRAM_API_KEY`)
- Opcional: `SECRET_KEY` para sesiones Flask y `SONIOX_MODEL` para cambiar el modelo por defecto

## Configuración

1. Clona el repositorio y entra en la carpeta del proyecto.
2. (Opcional) Crea y activa un entorno virtual.
3. Instala dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4. Crea un archivo `.env` en la raíz con tus claves:

    ```bash
    SONIOX_API_KEY=tu_clave_soniox
    DEEPGRAM_API_KEY=tu_clave_deepgram
    SECRET_KEY=clave_para_flask
    # SONIOX_MODEL=es_v2  (opcional)
    ```

## Ejecutar la aplicación web

```bash
python app.py
```

Abre http://localhost:5000 y alterna entre las pestañas Soniox y Deepgram para probar:

- Transcripción en vivo desde el micrófono con indicadores de estado y estadísticas.
- Subida drag & drop y procesamiento de archivos completos.
- Deepgram TTS con descarga directa del audio generado.


## Formatos compatibles

MP3, WAV, OGG, FLAC, AAC, WEBM, AMR, ASF, AIFF (normalizados automáticamente cuando es necesario).

## Problemas habituales

- **Sin audio o micrófono**: confirma permisos del navegador y que usas HTTPS en producción.
- **Errores de API**: revisa las claves en `.env` y que la cuenta tenga saldo/cuota.
- **Transcripción vacía**: verifica idioma, calidad del audio y formatos soportados.
