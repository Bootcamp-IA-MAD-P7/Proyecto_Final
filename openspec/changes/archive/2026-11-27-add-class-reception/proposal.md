# Proposal

## Why

E2 del [ROADMAP](../../../docs/ROADMAP.md), épica [#2](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/2): el profesorado tiene que poder enviar de verdad la grabación de una clase. El walking skeleton ([add-walking-skeleton](../add-walking-skeleton/proposal.md)) crea la clase y el trabajo, pero no guarda ni valida el audio, ni aplica la idempotencia, los límites de carga o la purga a los 14 días. Sin eso, E3 no tiene un audio que transcribir.

## What Changes

- **Contrato v0.2 (MINOR):** formatos admitidos, límites configurables de tamaño y duración, el error nuevo `invalid_audio_duration` y el estado `expired`, que pasa a producirse.
- **Recepción real del audio:** la API comprueba el tamaño, el formato por su contenido y la duración; guarda el audio en un almacenamiento privado con nombre opaco y crea la clase, el audio y el trabajo en la misma transacción antes de responder 202. `Idempotency-Key`, que sigue siendo opcional, devuelve la misma clase ante un reenvío idéntico y 409 si el contenido es otro.
- **Conservación limitada:** cada audio registra su recepción y su fecha de purga. `maintenance` borra a los 14 días el audio y sus temporales, deja en `expired` los trabajos sin terminar y elimina los archivos huérfanos de cargas fallidas.
- **Web:** la subida admite los formatos del contrato, muestra los errores de tamaño, formato y duración, y el estado `expired`.
- **Recepción acotada (#54):** la API rechaza antes de analizar el multipart los envíos cuyo cuerpo supera el tamaño del audio más un margen fijo para la envolvente. También corta una transmisión que declara un tamaño menor al real. Se aclaran Matroska, MOV y 3GP entre los contenedores ya admitidos por contenido, sin modificar el esquema ni la versión pública.

Fuera de alcance: los reintentos automáticos (`retry_wait` y `MAX_ATTEMPTS`), que llegan en E3 con los fallos reales de los modelos; la conversión de vídeo (MP4) a audio en el cliente; la conservación de transcripciones y resultados (PRD §14); la descarga del audio, y el despliegue ([ADR-0005](../../../docs/ADR/0005-local-only-environment.md)).

## Capabilities

### New Capabilities

- `audio-retention`: conservación del audio original durante 14 días, su purga y el bloqueo de los trabajos que caducan.

### Modified Capabilities

- `class-processing`: el envío de una clase pasa a guardar el audio y a validar su tamaño, formato y duración, y se añade la recepción idempotente.

## Impact

- **Requisitos:** RF-01 (recibir la grabación), RNF-02 (conservación limitada del audio) y RNF-05 (procesamiento diferido, que se mantiene).
- **Contratos:** `docs/CONTRACTS/coteach-ai-api.md` y `backend/openapi.json` pasan a 0.2.0; la web regenera sus tipos.
- **Documentación:** ARCHITECTURE §11 (se cierran los límites de carga), §4 (`app/storage/`) y §7 (volumen del audio); `backend/.env.example` y `.env.example`.
- **ADR:** aplica ADR-0002 (resultados tardíos invalidados) y ADR-0004 (volumen privado, purga reintentable). No necesita un ADR nuevo.
- **Dependencias:** las specs `class-processing` y `api-access` llegan a `openspec/specs/` con el archive de `add-walking-skeleton` (#38), así que este cambio solo se puede archivar después. La sección de integración añade el volumen a los archivos de Compose que también cambia #38 y depende de que esté en `dev`.
- **Épica:** #2. Una historia por sección de `tasks.md`, creadas al aprobar este plan.
