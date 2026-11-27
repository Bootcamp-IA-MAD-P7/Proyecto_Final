# Proposal

## Why

E3 del [ROADMAP](../../../docs/ROADMAP.md), épica [#3](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/3): cada clase recibida tiene que producir su transcripción con intervenciones por persona hablante y marcas temporales, y la web tiene que mostrarla. Hoy el worker ejecuta `FakePipeline`, que ignora el audio y devuelve siempre el mismo resultado sintético; desde E2 ([add-class-reception](../add-class-reception/proposal.md)) el audio ya se guarda validado, así que hay algo real que transcribir. Con los modelos reales llegan también los fallos transitorios, y con ellos los reintentos automáticos que E2 dejó para esta épica.

## What Changes

- **Pipeline por etapas real:** el worker procesa el audio guardado de cada clase por etapas, con adaptadores intercambiables (ADR-0003): normaliza con FFmpeg, transcribe con faster-whisper (Whisper small multilingüe), diariza con pyannote.audio (Community-1) y combina ambos resultados en la transcripción del contrato. Las copias de trabajo del audio se borran al terminar cada trabajo.
- **Personas hablantes de la sesión:** cada segmento se atribuye a una voz detectada, con identificadores de sesión en orden de primera intervención y sin asociarlas a participantes: la asociación es manual (RD-04). El número de participantes solo limita cuántas voces se buscan.
- **Reintentos automáticos:** un fallo transitorio deja el trabajo en `retry_wait` y se reintenta con esperas crecientes hasta `MAX_ATTEMPTS`; después, o ante un fallo que no es transitorio, el trabajo pasa a `failed`. Un trabajo que tumba el worker en cada intento no se reencola sin fin.
- **Web:** el resultado muestra la transcripción agrupada por persona hablante con sus marcas temporales, y el progreso muestra la espera de reintento.
- **Worker con modelos:** imagen propia del worker con las dependencias de inferencia en CPU, caché privada de los modelos, descarga de pesos separada del procesamiento y medición de recursos en el equipo de la demo (RNF-04).
- **Contrato:** sin cambios de campos (sigue en 0.2.0). La ficha documenta cómo se producen las personas hablantes y los segmentos, que `retry_wait` ya se produce y que el repaso sale vacío hasta E4.

Fuera de alcance: el análisis pedagógico real (E4); la asociación de personas hablantes a participantes y la corrección de la transcripción (E5); señalar los solapamientos en el contrato, que queda como limitación documentada; reanudar un reintento desde la etapa que falló; la ejecución con GPU; el reconocimiento de personas entre sesiones (RD-04), y el despliegue ([ADR-0005](../../../docs/ADR/0005-local-only-environment.md)).

## Capabilities

### New Capabilities

- `diarized-transcription`: qué contiene la transcripción de una clase procesada (texto con marcas temporales, intervenciones por persona hablante de la sesión) y qué pasa con las copias de trabajo del audio.

### Modified Capabilities

- `class-processing`: el seguimiento del trabajo por etapas pasa a reintentar los fallos transitorios (`retry_wait`, `MAX_ATTEMPTS`) y a dar por fallido un trabajo que tumba el worker en cada intento.
- `audio-retention`: los trabajos en espera de reintento también caducan cuando vence su audio.

## Impact

- **Requisitos:** RF-02 (transcripción diarizada), RF-04 (parte de transcripción del resultado), RNF-04 (eficiencia y recursos medidos), RD-04 (sesiones independientes) y RNF-01 (logs sin datos de la clase).
- **Contratos:** `docs/CONTRACTS/coteach-ai-api.md` documenta el comportamiento nuevo sin cambiar campos; `backend/openapi.json` no cambia.
- **Documentación:** ARCHITECTURE §2 (modelos medidos), §3 y §4 (adaptadores e imagen del worker), §5 (combinación, solapamientos y reintentos), §6 (caché de modelos y token de descarga), §7 (recursos medidos) y §11 (hardware y modelos); `backend/.env.example`, `.env.example` y el README.
- **ADR:** aplica ADR-0002 (reintentos de alcance pequeño y recuperación al arrancar) y ADR-0003 (modelos candidatos, adaptadores, versiones fijadas). No necesita un ADR nuevo salvo que la medición lleve a otros modelos.
- **Dependencias:** las specs `class-processing` y `audio-retention` llegan a `openspec/specs/` con los archive de `add-walking-skeleton` (#38) y `add-class-reception` (#49), así que este cambio se archiva después. Los reintentos tocan el worker y la `JobStore` que cambia la purga (#47). Sustituye al borrador `add-speaker-diarization` (rama `docs/E3-add-speaker-diarization`); su código de diarización (#52) es la base de la historia de diarización.
- **Épica:** #3. Una historia por sección de `tasks.md`, creadas al aprobar este plan.
