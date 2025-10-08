# Presentación: Deepgram vs Soniox

## Diapositiva 1 — Portada
- Presentación comparativa: Deepgram vs Soniox.
- Integrantes: 
    - Manuel Cardoso
    - Sebastian Orrego
    - Herney Quintero
    - Juan David Rodriguez
    - Franklin Aguirre


## Diapositiva 2 — Contenido
- Generalidades de las plataformas.
- Arquitectura y stack técnico.
- Funciones clave: Deepgram y Soniox.
- Casos de uso destacados.
- Precios y consideraciones de implementación.

## Diapositiva 3 — Generalidades de las plataformas
- **Deepgram**: plataforma empresarial de Voice AI con APIs unificadas para STT, TTS, agentes y analítica; reciente modelo Flux enfocado en conversación en tiempo real.
- **Soniox**: motor universal de voz que combina transcripción, traducción y entendimiento en 60+ idiomas; diseñado para funcionar en ambientes ruidosos desde el primer día.
- Ambas ofrecen trial con $200 USD en créditos API para comenzar sin costo inicial.

## Diapositiva 4 — Arquitectura y stack
- **Deepgram** integra Speech-to-Text, Text-to-Speech, Audio Intelligence y Voice Agent API en un solo endpoint, reduciendo latencia y orquestación externa.
- **Soniox** entrega un flujo unificado con salida a nivel de token en milisegundos y detección automática de idioma, hablantes y endpoints.
- Documentación REST/WebSocket completa; SDKs y playgrounds para pruebas rápidas en ambos proveedores.

## Diapositiva 5 — Funciones clave de Deepgram
- Modelos Nova-3, Flux y variantes optimizadas para precisión, velocidad o costo.
- Audio Intelligence con resúmenes, tópicos, intención y sentimiento sin requerir transcripción previa.
- Voice Agent API coordina STT, LLM y TTS en una sola llamada, permitiendo interrupciones naturales.
- Opciones de despliegue self-hosted y soporte para personalizar modelos según dominio.

## Diapositiva 6 — Funciones clave de Soniox
- Transcripción, traducción y comprensión en streaming con latencia sub-segundo.
- Reconocimiento robusto en entornos ruidosos, detección de hablantes y segmentación automática.
- Control por contexto (tokens de instrucciones) para adaptar vocabulario y respuestas.
- Cumplimiento SOC 2 Tipo II, HIPAA y procesamiento en memoria para escenarios sensibles.

## Diapositiva 7 — Casos de uso destacados
- **Contact centers**: Deepgram aporta analítica de voz a escala; Soniox optimiza agentes multilingües en vivo.
- **Salud**: Deepgram ofrece modelos personalizables; Soniox enfatiza privacidad HIPAA-ready.
- **Media/Podcasts**: Deepgram incluye smart formatting y búsquedas; Soniox entrega traducción simultánea y subtítulos rápidos.
- **Startups y wearables**: ambos proveen SDKs móviles; Soniox dispone de app lista para demostraciones.

## Diapositiva 8 — Precios Deepgram (2025)
- **Pay As You Go**: $200 USD de crédito inicial; sin mínimos.
- **Growth**: desde $4,000 USD/año con ahorro hasta 20% y límites ampliados.
- **Enterprise**: tarifas personalizadas; incluye modelos entrenados a medida y despliegue dedicado.
- **Tarifas STT (REST)**: Nova-3 monolingüe $0.0043/min; Flux promocional gratis hasta octubre; add-ons como Redaction desde $0.002/min.
- **TTS Aura-2**: $0.030/1k caracteres (PAYG), $0.027/1k caracteres (Growth).

## Diapositiva 9 — Precios Soniox (2025)
- Modelo tokenizado: aprox. $0.10/hora en modo async (≈30k tokens de audio) y $0.12/hora en streaming.
- Tasas por 1M tokens: audio $1.50 (async) / $2.00 (streaming); texto de salida $3.50 (async) / $4.00 (streaming).
- Créditos iniciales de $200 USD y esquema pay-as-you-go sin mínimos.
- App móvil: plan gratuito con 10 créditos semanales; Soniox Pro $19.99 USD/mes con transcripción ilimitada y procesamiento prioritario.

## Diapositiva 10 — Consideraciones de implementación
- **Deepgram**: límites de concurrencia (REST hasta 100) listos para proyectos piloto; soporte comunitario y canales enterprise; opciones de despliegue on-prem para requisitos regulatorios.
- **Soniox**: flujo tokenizado requiere ajustar presupuestos por tipo de token; latencia ultra baja facilita agentes de voz reactivos; cumplimiento regulatorio nativo acelera adopción en salud/finanzas.
- Integraciones sugeridas: normalización de audio, almacenamiento cifrado y métricas de calidad compartidas para comparar proveedores.

