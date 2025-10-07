# Soniox Speech-to-Text - Prueba de Concepto

Aplicación web completa para transcripción de audio a texto en español usando Soniox Speech-to-Text API (modelo `es_v2`).

## 🚀 Características

### Aplicación Web (Flask)
- 🎤 **Grabación en vivo** desde el micrófono con transcripción en tiempo real
- 📁 **Subir archivos** de audio con drag & drop
- 🔄 **WebSockets** para comunicación en tiempo real
- 📊 **Estadísticas** en vivo (palabras, caracteres, duración)
- 🎨 **Interfaz moderna** y responsiva

### Script de Línea de Comandos
- 🎯 **Transcripción de archivos** de audio
- ⏱️ **Timestamps precisos** por palabra
- 💾 **Exportación** a TXT
- 🇪🇸 **Optimizado para español** (modelo es_v2)

## 📋 Requisitos

- Python 3.8 o superior
- Cuenta en Soniox (https://console.soniox.com) - **Plan gratuito disponible**

## ⚙️ Instalación

### 1. Configuración Inicial

```bash
# Clonar el repositorio
git clone https://github.com/Yenreh/ConceptSoniox.git
cd ConceptSoniox

# Copiar archivo de configuración
cp .env.example .env
```

### 2. Obtener API Key (Gratis)

1. Ve a https://console.soniox.com/signup
2. Crea una cuenta gratuita
3. En "My First Project" → "API Keys"
4. Genera una nueva API Key
5. Copia la key en tu archivo `.env`:

```bash
SONIOX_API_KEY=tu_api_key_aqui
SECRET_KEY=tu_secret_key_para_flask  # Para Flask
```

### 3. Instalar Dependencias

```bash
# Para usar solo el script de línea de comandos
pip install -r requirements.txt

# Para usar la aplicación web Flask
pip install -r requirements_flask.txt
```

## 🎯 Uso

### Opción 1: Aplicación Web (Recomendado)

```bash
# Iniciar servidor Flask
python app.py
```

Abre tu navegador en **http://localhost:5000**

#### Funcionalidades Web

**Grabación en Vivo:**
1. Clic en "🎙️ Iniciar Grabación"
2. Permitir acceso al micrófono
3. Hablar en español
4. Ver transcripción en tiempo real
5. Clic en "⏹️ Detener" al terminar

**Subir Archivo:**
1. Arrastra un archivo de audio al área de carga
2. O haz clic para seleccionar archivo
3. La transcripción se mostrará automáticamente

### Opción 2: Script de Línea de Comandos

```bash
# Transcribir un archivo de audio
python speech_to_text.py
```

Coloca tu archivo de audio como `sample_audio.mp3` o modifica el script para usar otro archivo. El resultado se guardará en `transcription.txt`.

## 🎵 Formatos de Audio Soportados

- MP3
- WAV
- OGG
- FLAC
- AAC
- WEBM
- AMR
- ASF
- AIFF

## 🔧 Tecnologías

### Backend
- Flask + Flask-SocketIO
- Soniox Python SDK (gRPC)
- Python-dotenv

### Frontend
- HTML5 + CSS3
- JavaScript (Web Audio API)
- Socket.IO client
- Conversión WAV nativa en navegador

### API
- Soniox Speech-to-Text (modelo es_v2)
- Protocolo gRPC

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Navegador     │
│  (Micrófono)    │
│   Web Audio     │
│   API → WAV     │
└────────┬────────┘
         │ WebSocket
         ↓
┌─────────────────┐
│  Servidor Flask │
│   Socket.IO     │
└────────┬────────┘
         │ gRPC
         ↓
┌─────────────────┐
│   Soniox API    │
│  (modelo es_v2) │
└─────────────────┘
```

## 📂 Estructura del Proyecto

```
ConceptSoniox/
├── app.py                    # Servidor Flask principal
├── speech_to_text.py         # Script CLI
├── templates/
│   └── index.html           # Interfaz web
├── requirements.txt         # Dependencias básicas
├── requirements_flask.txt   # Dependencias web
├── .env.example            # Template de configuración
├── .gitignore              # Archivos ignorados
└── README.md               # Este archivo
```

## 🐛 Troubleshooting

### No se puede acceder al micrófono
- Permitir acceso al micrófono en el navegador
- En producción, requiere HTTPS (no HTTP)
- Verificar permisos del sistema operativo

### La transcripción no aparece
- Verificar que `SONIOX_API_KEY` sea correcta en `.env`
- Revisar la consola del navegador (F12) para errores
- Verificar los logs del servidor Flask en la terminal

### Audio sin transcribir
- Verificar que el audio esté en español
- Asegurar buena calidad de audio (sin ruido)
- Comprobar formato de audio soportado

## 🚀 Mejoras Futuras

- [ ] Soporte para múltiples idiomas (es_v2, en_v2)
- [ ] Exportar transcripción (TXT, JSON, SRT)
- [ ] Visualización de timestamps
- [ ] Edición de transcripción
- [ ] Guardar sesiones
- [ ] Autenticación de usuarios
- [ ] Migración a nueva API multilingüe

## 📚 Documentación Oficial

- **API Legacy (esta implementación)**: https://soniox.com/docs/speech-to-text-legacy/api-frameworks/grpc
- **Nueva API (60+ idiomas)**: https://soniox.com/docs/stt/get-started
- **Ejemplos Python**: https://github.com/soniox/soniox_examples
- **Discord**: https://discord.gg/rWfnk9uM5j

## 📝 Notas

- Esta implementación usa la **API Legacy** con modelo `es_v2` (español)
- Para soporte multilingüe (60+ idiomas), considera migrar a la nueva API
- Los archivos de audio están excluidos del control de versiones
- El archivo `.env` está excluido por seguridad
- Plan gratuito disponible para pruebas
- Para producción, revisar límites en documentación oficial

## 📄 Licencia

Este es un proyecto de prueba de concepto para fines educativos.

## 👤 Autor

**Yenreh**
- GitHub: [@Yenreh](https://github.com/Yenreh)
- Repositorio: [ConceptSoniox](https://github.com/Yenreh/ConceptSoniox)
