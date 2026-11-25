# Tasks

Plan de la funcionalidad `add-speaker-diarization` (E3, épica #3). Una sección por historia: primero la prueba básica de diarización, luego la integración en el pipeline y el worker, luego las pruebas de calidad (DER/atribución) y al final la integración de extremo a extremo. El diseño está en [design.md](design.md) y la spec en `specs/diarization/spec.md`.

## 1. Prueba básica de diarización con pyannote.audio (backend) · #20 (US-012)

**Criterios de aceptación:**
- Existe `backend/scripts/test_diarization.py` que, dado un archivo de audio corto con dos hablantes, separa las intervenciones e imprime, para cada segmento detectado: `inicio - fin: speaker_id`.
- Usa pyannote.audio (speaker-diarization-3.1) como motor de diarización; si no está disponible, usa una alternativa de código abierto (librosa + scikit-learn) que funcione en Windows sin GPU.
- No requiere credenciales ni datos reales; se ejecuta sobre audio sintético o de prueba.
- `make backend-lint` y `make backend-test` pasan.

**Depende de:** —

- [x] 1.1 Añadir pyannote.audio y sus dependencias a `backend/requirements.txt` (o a un grupo opcional, si el modelo requiere entorno específico).
- [x] 1.2 Implementar o adaptar `backend/scripts/test_diarization.py` para usar pyannote.audio y separar 2 hablantes, imprimiendo `speaker_id` por segmento.
- [x] 1.3 Probar el script con audio corto de 2 hablantes y verificar la salida `speaker_id`.
- [x] 1.4 Documentar en el script cómo instalar los pesos y qué hacer si no hay GPU.

## 2. Etapa DIARIZING en inference pipeline y worker (backend)

**Nota:** el diseño está en [design.md](design.md); la spec del cambio vive en `openspec/changes/add-speaker-diarization/specs/diarization/spec.md` y se aplica al archivar.

**Criterios de aceptación:**
- El `InferencePipeline` implementa la etapa de diarización y devuelve `Transcript` con `speakers` (`speaker_id`, `participant_id` nullable) y `segments` (`segment_id`, `start_ms`, `end_ms`, `speaker_id`, `text`).
- El worker avanza un trabajo por la etapa `DIARIZING` y la completa o la mueve a `failed` con un código de error del contrato (`processing_failed`, `invalid_audio`).
- Cada `speaker_id` de segmento está declarado en `speakers`; `end_ms > start_ms`; no se inventan hablantes por participantes en silencio.
- `make backend-test` y `make backend-lint` pasan.

**Depende de:** 1

- [x] 2.1 Implementar el adaptador de diarización sobre `InferencePipeline` con pyannote.audio y fallback a la alternativa de código abierto (`backend/app/inference/diarization.py`).
- [x] 2.2 Implementar el cruce de intervalos entre diarización y transcripción para atribuir `speaker_id` a cada segmento (`RealPipeline`).
- [x] 2.3 Conectar el worker con la etapa `DIARIZING`: avanzar, completar con `Result` o fallar con `JobError` (`app/worker/__main__.py`).
- [x] 2.4 Añadir pruebas unitarias de la etapa de diarización con audio sintético y de los casos de error (`tests/test_diarization_pipeline.py`).

## 3. Pruebas de DER y atribución con audio anotado (backend)

**Criterios de aceptación:**
- Pruebas unitarias de intervalos: `start_ms`/`end_ms` coherentes, fin mayor que inicio, segmentos no vacíos.
- Prueba del modelo real con ruido, silencio y solapamiento; se mide DER y atribución frente a referencia anotada.
- Verificar que un participante en silencio no genera un `speaker_id` inventado y que en solapamiento no se inventa identidad (admite `participant_id` nulo).
- Conservar entrada sintética, resultado esperado y resultado observado como evidencia reproducible.
- `make backend-test` y `make backend-lint` pasan.

**Depende de:** 2

- [ ] 3.1 Crear casos de prueba con audio anotado (referencia de `speaker_id` y `start_ms`/`end_ms` esperados).
- [ ] 3.2 Implementar medición de DER y atribución en las pruebas.
- [ ] 3.3 Añadir pruebas de borde: silencio total, un solo hablante, solapamiento, audio muy corto.
- [ ] 3.4 Guardar fixtures de entrada, esperado y observado en `backend/tests/fixtures/` o similar.

## 4. Integración de extremo a extremo con transcripción (integración)

**Criterios de aceptación:**
- Una clase enviada a la API avanza por todas las etapas (`queued → ... → DIARIZING → ... → ready_for_review`) y el resultado incluye la transcripción diarizada con `speaker_id`.
- La integración job → transcripción → diarización funciona de extremo a extremo contra el stack real (API + worker + job store).
- `make ci` pasa y `verify` del cambio no deja discrepancias con las specs.
- ARCHITECTURE §3 y §4 reflejan el componente worker y la etapa de diarización.

**Depende de:** 1, 2, 3

- [ ] 4.1 Verificar que el worker completo (con job store de PostgreSQL) procesa una clase hasta `ready_for_review` incluyendo diarización.
- [ ] 4.2 Comprobar que el resultado devuelto por `GET /v1/classes/{class_id}/result` incluye `Transcript` con `speakers` y `segments` con `speaker_id`.
- [ ] 4.3 Ejecutar `make ci` completo y corregir fallos.
- [ ] 4.4 Actualizar ARCHITECTURE §3, §4 y §7 si es necesario.
- [ ] 4.5 Ejecutar `verify`, `sync` y `archive` del cambio (skill `pull-requests`).
