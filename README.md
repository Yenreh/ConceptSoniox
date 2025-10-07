# Prueba de Concepto - Soniox Speech-to-Text API (Legacy)

Prueba de concepto simple para la API Legacy de Soniox Speech-to-Text, que transcribe audio a texto usando IA. **Usa el modelo `es_v2` optimizado para español**.

> **Nota**: Esta implementación usa la API Legacy (gRPC). Para la nueva API multilingüe con 60+ idiomas, consulta: https://soniox.com/docs/stt/get-started

## Características

- **Transcripción de audio a texto** con alta precisión
- **Modelo optimizado para español** (`es_v2`)
- **Timestamps precisos** por palabra
- API basada en gRPC (baja latencia)
- Múltiples formatos de audio soportados
- **Plan gratuito disponible**

## Requisitos

- Python 3.8 o superior
- Cuenta en Soniox (https://console.soniox.com) - **Tiene plan gratuito**

## Instalación

1. Clona este repositorio o descarga los archivos

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Obtén tu API Key (gratis):
   - Ve a https://console.soniox.com/signup
   - Crea una cuenta gratuita
   - En el proyecto "My First Project", ve a "API Keys"
   - Genera una nueva API Key

4. Configura las variables de entorno:
```bash
cp .env.example .env
```

5. Edita el archivo `.env` y agrega tu API Key:
```
SONIOX_API_KEY=tu_api_key_aqui
```

## Uso

### Script básico

1. Coloca un archivo de audio en el directorio (por ejemplo: `sample_audio.mp3`)
   - Formatos soportados: mp3, wav, ogg, flac, webm, aac, amr, asf, aiff

2. Ejecuta el script:
```bash
python speech_to_text.py
```

El script transcribirá el audio y guardará el resultado en `transcription.txt`.

### Ejemplos avanzados

Para explorar características avanzadas:
```bash
python ejemplos_avanzados.py
```

Este script incluye ejemplos de:
- Transcripción básica
- Transcripción con timestamps por palabra
- Identificación automática de idioma
- Simulación de transcripción en tiempo real
- Exportación en múltiples formatos (TXT, JSON)
- Guardado de resultados con metadata

## Idiomas Soportados

Esta implementación usa la **API Legacy** que soporta **español** con el modelo `es_v2`.

**Modelos disponibles en API Legacy:**
- `es_v2` - Español (usado en este proyecto)
- `en_v2` - Inglés

**Para soporte multilingüe (60+ idiomas)**, considera migrar a la nueva API:
- Documentación: https://soniox.com/docs/stt/get-started
- Ejemplos: https://github.com/soniox/soniox_examples

## Modelos Disponibles (Legacy)

### `es_v2` (Usado en este proyecto)
- **Optimizado para español**
- Alta precisión
- Baja latencia con gRPC
- Manejo mejorado de acrónimos y números en español

## API en Tiempo Real

Para transcripción en tiempo real, considera usar la **nueva API de Soniox**:
- WebSocket API: https://soniox.com/docs/stt/rt/real-time-transcription
- Soporte multilingüe
- Traducción en tiempo real

## Documentación Oficial

- **API Legacy (esta implementación)**: https://soniox.com/docs/speech-to-text-legacy/api-frameworks/grpc
- **Nueva API (recomendada)**: https://soniox.com/docs/stt/get-started
- **Ejemplos Python**: https://github.com/soniox/soniox_examples
- **GitHub**: https://github.com/soniox
- **Discord**: https://discord.gg/rWfnk9uM5j

## Características Avanzadas

### Timestamps por Palabra
```python
for word in result.words:
    print(f"{word.start_ms/1000:.2f}s: {word.text}")
```

## Migración a la Nueva API

Si necesitas soporte multilingüe o características avanzadas, considera migrar:

```bash
# Clonar ejemplos de la nueva API
git clone https://github.com/soniox/soniox_examples
cd soniox_examples/speech_to_text/python

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar ejemplo multilingüe
python soniox_realtime.py --audio_path ../assets/coffee_shop.mp3
```

## Formatos de Audio Soportados

### Auto-detectados (sin configuración)
- MP3, WAV, OGG, FLAC, AAC, WEBM, AMR, ASF, AIFF

### Raw audio (requiere configuración)
- PCM (varios formatos)
- mulaw, alaw

## Casos de Uso

- **Transcripción de contenido en español**
- **Subtítulos para videos en español**
- **Transcripción de reuniones** (español)
- **Análisis de llamadas** telefónicas en español
- **Documentación** de contenido de audio
- **Búsqueda en contenido de audio**

> Para casos de uso multilingües, usa la nueva API

## Límites y Cuotas

Consulta los límites actuales en: https://soniox.com/docs/stt/rt/limits-and-quotas

El plan gratuito incluye acceso a la API para pruebas.

> **Nota**: Esta es la API Legacy. Para características más avanzadas y mejor soporte, considera la nueva API.

## Documentación Oficial

- **API Legacy (esta implementación)**: https://soniox.com/docs/speech-to-text-legacy/api-frameworks/grpc
- **Nueva API (recomendada)**: https://soniox.com/docs/stt/get-started
- **Ejemplos Python**: https://github.com/soniox/soniox_examples
- **GitHub**: https://github.com/soniox
- **Discord**: https://discord.gg/rWfnk9uM5j

## Ejemplos en GitHub

Repositorio oficial con ejemplos:
```bash
git clone https://github.com/soniox/soniox_examples
cd soniox_examples/speech_to_text/python
```

## Comparación: API Legacy vs Nueva API

| Característica | API Legacy (esta) | Nueva API |
|---------------|-------------------|-----------|
| Protocolo | gRPC | WebSocket/HTTP |
| Idiomas | Español (es_v2) | 60+ idiomas |
| Detección idioma | No | Automática |
| Traducción | No | Sí |
| Tiempo real | Limitado | Full WebSocket |
| Recomendado | Para español simple | Para producción |

## Soporte

Si necesitas ayuda:
- Discord: https://discord.gg/rWfnk9uM5j
- GitHub: https://github.com/soniox
- Documentación: https://soniox.com/docs

## Notas

- Los archivos de audio (`.mp3`, `.wav`, etc.) están excluidos del control de versiones
- El archivo `.env` con tu API key está excluido por seguridad
- Soniox ofrece plan gratuito para pruebas
- Para producción, revisa los límites en la documentación oficial
