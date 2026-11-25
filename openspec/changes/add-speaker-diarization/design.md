# Design

## Context

Ver [proposal.md](proposal.md). El *walking skeleton* de E1 ya levanta API, worker y job store con un pipeline simulado (`FakePipeline`) y el contrato v0.1 declara `Transcript`, `Segment` y `Speaker`. El lifecycle del trabajo ya incluye `DIARIZING` entre `TRANSCRIBING` y `ANALYZING`. El ADR-0003 propone pyannote.audio (speaker-diarization-community-1) como modelo candidato para la diarización, con evaluación de errores y acceso a pesos. Este cambio sustituye el paso simulado de diarización por una implementación real sobre ese modelo, sin rediseñar el worker, el job store ni el contrato.

## Goals / Non-Goals

**Goals:**

- Integrar la diarización real como etapa `DIARIZING` del pipeline de inferencia, producida por el worker existente.
- Producir `Speaker(speaker_id, participant_id?: null)` y `Segment(segment_id, start_ms, end_ms, speaker_id, text)` conforme al contrato v0.1.
- Proveer una prueba básica (`backend/scripts/test_diarization.py`) con pyannote.audio sobre audio corto que separe 2 hablantes e imprima `speaker_id`.
- Cubrir RF-02 y RD-04: no inventar voz por participante en silencio, no inventar identidad en solapamiento, admitir asignación nula.

**Non-Goals:** guardar o validar el audio (E2); análisis pedagógico real (E4); corrección, aprobación y publicación persistentes (E5); asignación automática de `speaker_id` a `participant_id` (historia 017); reconocimiento biométrico entre sesiones (ADR-0003); despliegue en producción (ADR-0005).

## Decisions

### Motor de diarización

Se usa **pyannote.audio** con el modelo **speaker-diarization-community-1** (ADR-0003), por ser open source, tener licencia CC-BY-4.0 y estar referenciado en la arquitectura. Se evalúa acceso a pesos y compatibilidad antes de fijarlo como definitivo; el adaptador es intercambiable para sustituirlo por otro modelo tras medir.

### Integración en el pipeline

La `InferencePipeline` existente ya declara el protocolo de stages y el `PipelineOutput` con `transcript` y `analysis`. La diarización se añade como una etapa más del pipeline, que recibe el audio y devuelve los `speaker_id` y sus intervalos. El worker ya recorre `NORMALIZING → TRANSCRIBING → DIARIZING → ANALYZING`; solo se implementa la lógica de la etapa `DIARIZING`.

### Cruce de intervalos

La diarización produce intervalos de `speaker_id`; la transcripción produce intervalos de texto. El worker cruza ambos por solapamiento temporal para atribuir cada segmento de texto a un `speaker_id`, sin modificar la etapa de transcripción.

### Contrato sin cambios

El contrato v0.1 ya declara las formas necesarias (`speakers` con `speaker_id` y `participant_id` nullable; `segments` con `speaker_id` existente). No se crea ni se modifica contrato alguno (skill `contracts` no aplica).

### Prueba de entrada

`backend/scripts/test_diarization.py` es un script standalone (sin torchcodec, para Windows) que carga audio con librosa, extrae MFCC, aplica clustering jerárquico con 2 clusters y agrupa frames consecutivos del mismo hablante en segmentos, imprimiendo `speaker_id`. Es la prueba básica de US-012 y se ejecuta sin necesidad de GPU ni de pyannote.audio instalado; la versión con pyannote.audio se añade como prueba de integración del modelo real.

## Interfaces internas

- **`InferencePipeline`** (`backend/app/inference/pipeline.py`): protocolo ya declarado. La diarización se implementa como una etapa que devuelve `PipelineOutput.transcript` con `speakers` y `segments`.
- **`JobStore`** (`backend/app/jobs/store.py`): ya declara `claim_next`, `advance`, `complete` y `fail`. El worker avanza por `DIARIZING` usando estos mismos métodos; no se cambia la interfaz.
- **`FakePipeline`** (`backend/app/inference/fake.py`): se mantiene para tests y para entornos sin modelos reales; E3 lo sustituye por el pipeline real solo en la etapa de diarización.

## Riesgos / compensaciones

- **Pesos y licencia de pyannote.audio:** requieren comprobar condiciones de acceso y atribución antes de aceptar el modelo como definitivo (ADR-0003).
- **Hardware/GPU:** la diarización real puede necesitar GPU; se documenta como requisito de inicio de US-012 y no bloquea la prueba básica con librosa+scikit-learn.
- **Solapamientos y cambios de idioma:** son riesgos conocidos del modelo candidato; se miden con clases de 30 y 60 minutos antes de fijar umbrales de aceptación.

## Open Questions

- ¿Qué umbral de DER y atribución se considera aceptable para la demo de diciembre?
- ¿Se necesita GPU en el entorno de desarrollo o solo en la máquina de la persona responsable?
- ¿Quién verifica el consentimiento antes de procesar audio real (PRD §14)?
