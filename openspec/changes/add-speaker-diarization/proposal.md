# Proposal

## Why

E3 del [ROADMAP](../../../docs/ROADMAP.md), épica [#3](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/3), es «Transcripción diarizada consultable»: el sistema debe producir una transcripción con intervenciones separadas por persona hablante y marcas temporales, de modo que el profesorado pueda distinguir quién habla en cada momento y corregir atribuciones ambiguas. Este cambio cubre la historia [#20 (US-012 — Diarización e integración de hablantes)](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/20), cerrada como *not planned* y cuya propuesta sirve de entrada al plan.

El [PRD](../../../docs/PRD.md) ya declara RF-02 («Generar una transcripción diarizada de la sesión») y el glosario define «Transcripción diarizada». El [contrato v0.1](../../../docs/CONTRACTS/coteach-ai-api.md) ya declara `Transcript`, `Segment(speaker_id, start_ms, end_ms, text)` y `Speaker(speaker_id, participant_id)`, y `JobStage` ya incluye `DIARIZING` en el lifecycle del trabajo. El ADR-0003 apunta a pyannote.audio (speaker-diarization-community-1) como modelo candidato para la diarización.

Este cambio implementa la diarización real (fuera de alcance del *walking skeleton* de E1) como una funcionalidad propia de E3, integrada en el worker y en el pipeline de inferencia existentes.

## What Changes

- **`backend/app/inference/`:** implementación real de `InferencePipeline` para la etapa de diarización, con pyannote.audio como motor y un adaptador intercambiable, que produce `Speaker` y `Segment` con `speaker_id` de sesión y `participant_id` nullable.
- **`backend/app/worker/`:** el worker avanza por la etapa `DIARIZING` y cruza los intervalos de diarización con los de transcripción, conforme al contrato.
- **`backend/scripts/test_diarization.py`:** prueba básica con pyannote.audio sobre audio corto que separa 2 hablantes e imprime `speaker_id` por segmento (historia de entrada de US-012).
- **`backend/tests/`:** pruebas unitarias de intervalos y de la etapa de diarización, y pruebas de DER y atribución frente a referencia con audio anotado.
- **`openspec/specs/`:** spec de comportamiento de la diarización (delta de specs sobre el contrato existente).

Fuera de alcance: guardar, validar y purgar el audio (E2); análisis pedagógico real (E4); corrección, aprobación y publicación persistentes (E5); asignación automática de `speaker_id` a `participant_id` (pertenece a la historia 017, edición de asociaciones); reconocimiento biométrico entre sesiones (ADR-0003).

## Capabilities

### New Capabilities

- `diarization`: detectar cuántas personas hablan en una grabación, separar sus intervenciones con marcas temporales y asociar cada segmento a un `speaker_id` de sesión.

### Modified Capabilities

Ninguna; el contrato v0.1 ya declara las formas de `Transcript`, `Segment` y `Speaker`.

## Impact

- **Requisitos:** RF-02 (transcripción diarizada), RD-04 (no inventar voz por participante en silencio, no inventar identidad en solapamiento o duda, admitir asignación nula).
- **Documentación:** `docs/ARCHITECTURE.md` §3 y §4 (componente worker, etapa diarización); `docs/ADR/0003-private-inference.md` (modelo candidato pyannote.audio); `docs/CONTRACTS/coteach-ai-api.md` no cambia de forma, solo se especifica su uso en la diarización.
- **ADR:** aplica ADR-0003 (inferencia privada y modelos candidatos). No necesita un ADR nuevo salvo que se elija un modelo distinto a pyannote.audio.
- **Épica:** #3. Una historia por sección de `tasks.md`, creadas al aprobar este plan. La primera historia cubre US-012 (#20).
