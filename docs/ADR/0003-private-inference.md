# ADR-0003: Private staged inference

- **Estado:** Aceptado
- **Fecha:** 2026-11-24
- **Decisores:** Equipo de tres personas; CoTeach/Lay para restricciones de producto y datos.
- **Relacionado:** RF-02, RF-03; RNF-03, RNF-04; ADR-0001. Sin Issue: fase 1.

## Contexto

Las fuentes exigen software libre y privacidad, pero no fijan modelos, hardware, presupuesto ni idiomas imprescindibles. La calidad de diarización y repaso debe medirse con clases reales autorizadas.

## Decisión

Evaluar faster-whisper con Whisper small multilingüe, pyannote.audio Community-1 y Qwen3-8B cuantizado servido por llama.cpp. Etapas secuenciales, adaptadores intercambiables, validación JSON y fragmentación por tokens. Usar GPU local primero; GPU remota privada solo tras aprobación de coste y tratamiento de datos. Registrar versiones, parámetros y hashes. Nombres de entrada se asignan manualmente a hablantes cuando no existe evidencia fiable; no reconocimiento biométrico entre sesiones.

El detalle operativo está en [ARCHITECTURE](../ARCHITECTURE.md).

## Alternativas consideradas

- Whisper large: comparar si small no alcanza calidad y hay memoria; no imponer coste antes de medir.
- WhisperX: integra alineamiento y diarización, pero amplía dependencias; evaluar si el cruce de segmentos no basta.
- API comercial: reduce operación pero requiere validar transferencias, soberanía y condiciones; no base propuesta.
- Solo CPU: útil en pruebas cortas, capacidad para clases completas no demostrada.

## Consecuencias

faster-whisper permite CPU/GPU y cuantización; fijar dependencias CUDA compatibles. Community-1 publica licencia CC-BY-4.0 y requiere comprobar condiciones de acceso/atribución de pesos; no confundir licencia de modelo y biblioteca. Qwen3-8B publica Apache-2.0; verificar también distribución cuantizada y dependencias. El cumplimiento de software libre requiere revisión de todo el conjunto antes de aceptar este ADR. No hay benchmark ni VRAM mínima probada; catalán, chino, cambios de idioma y solapamientos son riesgos. Fuentes: https://github.com/SYSTRAN/faster-whisper ; https://huggingface.co/pyannote/speaker-diarization-community-1 ; https://huggingface.co/Qwen/Qwen3-8B ; https://github.com/ggml-org/llama.cpp .
