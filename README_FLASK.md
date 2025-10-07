# Aplicación Web de Transcripción en Vivo

Interfaz web con Flask para transcripción de audio en vivo usando Soniox Speech-to-Text API.

## Características

- 🎤 **Grabación en vivo** desde el micrófono
- 📁 **Subir archivos** de audio (MP3, WAV, OGG, WEBM, FLAC)
- 🔄 **Transcripción en tiempo real** con WebSockets
- 📊 **Estadísticas** en vivo (palabras, caracteres, duración)
- 🎨 **Interfaz moderna** y responsiva
- 🇪🇸 **Optimizado para español** (modelo es_v2)

## Instalación

1. Instalar dependencias adicionales:
```bash
pip install -r requirements_flask.txt
```

2. Configurar la API key en `.env`:
```bash
SONIOX_API_KEY=tu_api_key_aqui
SECRET_KEY=tu_secret_key_para_flask
```

## Uso

1. Iniciar el servidor:
```bash
python app.py
```

2. Abrir en el navegador:
```
http://localhost:5000
```

## Funcionalidades

### Grabación en Vivo
1. Haz clic en "🎙️ Iniciar Grabación"
2. Permite el acceso al micrófono
3. Habla en español
4. La transcripción aparecerá en tiempo real
5. Haz clic en "⏹️ Detener" cuando termines

### Subir Archivo
1. Arrastra un archivo de audio al área de carga
2. O haz clic para seleccionar un archivo
3. La transcripción se mostrará automáticamente

### Limpiar
- Haz clic en "🗑️ Limpiar" para borrar la transcripción actual

## Tecnologías

- **Backend**: Flask + Flask-SocketIO
- **Frontend**: HTML5 + JavaScript + Socket.IO
- **API**: Soniox Speech-to-Text (modelo es_v2)
- **Audio**: MediaRecorder API (navegador)

## Formatos de Audio Soportados

- MP3
- WAV
- OGG
- WEBM
- FLAC
- AAC

## Notas

- La grabación en vivo envía chunks de audio cada 2 segundos
- Funciona mejor con audio claro y sin ruido de fondo
- El modelo es_v2 está optimizado para español
- Requiere HTTPS en producción para acceso al micrófono

## Troubleshooting

### No se puede acceder al micrófono
- Asegúrate de permitir el acceso al micrófono en tu navegador
- En algunos navegadores, necesitas HTTPS (no HTTP)

### La transcripción no aparece
- Verifica que tu SONIOX_API_KEY sea correcta
- Revisa la consola del navegador para errores
- Verifica los logs del servidor Flask

## Arquitectura

```
Cliente (Navegador)
    ↓ WebSocket
Servidor Flask (app.py)
    ↓ gRPC
Soniox API (es_v2)
```

## Mejoras Futuras

- [ ] Soporte para múltiples idiomas
- [ ] Exportar transcripción (TXT, JSON, SRT)
- [ ] Timestamps visuales
- [ ] Edición de transcripción
- [ ] Guardar sesiones
- [ ] Autenticación de usuarios
