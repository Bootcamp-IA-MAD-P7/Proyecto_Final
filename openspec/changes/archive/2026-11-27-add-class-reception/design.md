# Design

## Context

Ver [proposal.md](proposal.md). El walking skeleton ([add-walking-skeleton](../add-walking-skeleton/design.md)) ya tiene la API, la `JobStore` de PostgreSQL, el worker con `FakePipeline`, `maintenance` con un ciclo vacío y el contrato v0.1, que declara 409, 413 y 415 en `POST /v1/classes` sin aplicarlos. Este cambio añade el audio real a ese recorrido sin tocar el pipeline: `FakePipeline` sigue devolviendo el resultado sintético hasta E3.

Mientras se planifica, la integración del skeleton (#38) está en curso y cambia los archivos de Compose, la configuración del backend y ARCHITECTURE §3, §4 y §7.

## Goals / Non-Goals

**Goals:**

- Guardar el audio de cada clase de forma privada, validado por su contenido, con límites configurables.
- Recepción idempotente por quien envía y su clave.
- Purgar el audio a los 14 días y caducar los trabajos sin terminar, desde `maintenance`.

**Non-Goals:** reintentos automáticos (`retry_wait`, `MAX_ATTEMPTS`), que llegan en E3; normalizar el audio para los modelos (E3); conservación de transcripciones y resultados (PRD §14); descargar el audio; convertir vídeo en el cliente.

## Decisions

### Formatos y límites

Decididos con el equipo al planificar (cierran la pregunta de ARCHITECTURE §11 «Límites de carga»):

| Límite | Valor por defecto | Variable |
|---|---|---|
| Formatos | Opus (Ogg, WebM o Matroska), MP3 y AAC (M4A, MP4, MOV o 3GP, solo con audio) | lista fija en el código y en el contrato |
| Tamaño máximo | 150 MB | `UPLOAD_MAX_BYTES` |
| Duración mínima | 1 minuto | `UPLOAD_MIN_SECONDS` |
| Duración máxima | 2 horas | `UPLOAD_MAX_SECONDS` |
| Conservación | 14 días (RNF-02) | `AUDIO_RETENTION_DAYS` |

El cliente envía audio ya comprimido (por ejemplo, con FFmpeg); convertir MP4 de vídeo o MP3 a ese audio en el cliente es una herramienta futura, fuera de este cambio. Se admiten varios formatos porque el paso de normalización de E3 los convierte todos con FFmpeg, así que no cuesta más que admitir uno.

### Validación del audio

- **Tamaño:** la API copia la parte `audio` a un temporal contando bytes y corta con 413 en cuanto supera `UPLOAD_MAX_BYTES`, sin leer el resto.
- **Formato y duración:** `ffprobe` sobre el temporal. El contenedor y el códec tienen que estar en la lista; un archivo que no se puede leer, sin pista de audio o con vídeo es 415 `unsupported_audio`. La extensión y el `Content-Type` no se tienen en cuenta. La duración fuera de los límites es 422 `invalid_audio_duration`.
- **Orden de los errores:** 401 y 403; 422 de metadatos (con la precedencia de v0.1); 413; 415; 422 `invalid_audio_duration`; 409 `idempotency_conflict`. Así un envío con varios problemas recibe siempre el mismo error. Con el límite temprano de #54, un cuerpo que supera el límite de recepción se rechaza con 413 antes de analizar los metadatos, como se decide más abajo y documenta el contrato; la precedencia anterior se aplica cuando el cuerpo cabe en ese límite.
- **FFmpeg en la imagen:** la imagen de `backend` (que usan también `worker` y `maintenance`) instala FFmpeg, que ARCHITECTURE §2 ya da como Objetivo. Sin Docker, `ffprobe` tiene que estar en el `PATH`; los tests que lo necesitan se saltan con un aviso si falta, y en `make ci` siempre se ejecutan.
- **Audios de prueba:** los tests generan audios sintéticos (tonos o silencio) con `ffmpeg` al ejecutarse; no se versiona audio en el repositorio.

### Límite temprano de la recepción (#54)

- Antes de que FastAPI analice `multipart/form-data`, un middleware dedicado a `POST /v1/classes` autentica y autoriza al emisor y compara `Content-Length` con `UPLOAD_MAX_BYTES + 64 KiB`. Los 64 KiB cubren las cabeceras, límites multipart y el JSON de metadatos; no son bytes adicionales permitidos para el archivo.
- Si falta `Content-Length` o declara menos bytes de los enviados, el middleware cuenta los fragmentos ASGI y responde 413 `audio_too_large` al superar ese mismo límite, sin solicitar el resto del cuerpo. Los rechazos tempranos no crean temporales, clases ni trabajos.
- Tras el margen de la envolvente, `receive_audio` conserva su contador exacto sobre la parte `audio`: un archivo de exactamente `UPLOAD_MAX_BYTES` es válido y uno de un byte más sigue recibiendo 413, aunque el multipart completo caiga dentro del margen.
- La autenticación y la autorización preceden al límite temprano. Para una persona autorizada, un cuerpo que excede el límite de recepción se rechaza antes de analizar metadatos, porque continuar hasta la validación de formulario anularía la protección frente a cuerpos grandes.
- Los contenedores ya aceptados por `ffprobe` se expresan de forma completa: Opus en Ogg, WebM o Matroska; MP3; y AAC en M4A, MP4, MOV o 3GP. El contenedor y códec se comprueban por contenido y los vídeos siguen rechazándose.

### Almacenamiento privado

- **`app/storage/`** declara `AudioStorage` (escribir un temporal, confirmarlo con un nombre opaco, borrar, listar los archivos) con una implementación en disco bajo `AUDIO_STORAGE_DIR`. Es la abstracción que pide ARCHITECTURE para cambiar de almacenamiento sin tocar la API.
- **Nombres opacos:** el archivo se guarda como `<audio_id>` sin extensión ni datos de la clase; la ruta nunca sale en el contrato ni en los logs.
- **Orden de la carga** (ARCHITECTURE «recepción»): temporal → validación → mover al almacenamiento → una transacción que crea clase, audio y trabajo → 202. Si la transacción falla, la API borra el archivo; si el proceso muere antes, el archivo queda huérfano y lo limpia `maintenance`.
- **Tabla `audio_assets`:** `audio_id`, `class_id`, `storage_key`, `format`, `size_bytes`, `duration_seconds`, `sha256`, `received_at`, `expires_at`, `deleted_at`. Migración nueva de Alembic.
- **Volumen:** en Compose, un volumen con nombre montado en `backend`, `worker` y `maintenance`, fuera de Git y de las copias de seguridad (ADR-0004). Lo añade la sección de integración, después de #38, que cambia esos mismos archivos.

### Idempotencia

- Clave única por (`submitted_by`, `Idempotency-Key`), guardada con la clase junto a una huella del contenido: el `sha256` del audio y de los metadatos normalizados.
- Misma clave y misma huella: 202 con la clase y el trabajo existentes, sin guardar el audio otra vez. Misma clave y otra huella: 409. La clave de otra persona no choca.
- La cabecera sigue siendo opcional: hacerla obligatoria sería un cambio incompatible del contrato (MAJOR).

### Purga y caducidad

- **Ciclo de `maintenance`** (cada `MAINTENANCE_INTERVAL_SECONDS`, también al arrancar antes del primer intervalo):
  1. Marca como `expired` los trabajos sin terminar (`queued` o en una etapa) cuyo audio ha vencido.
  2. Borra el archivo de cada audio vencido sin `deleted_at` y registra `deleted_at`; si el borrado falla, lo registra en el log sin datos de la clase y lo reintenta en el ciclo siguiente.
  3. Borra los archivos del almacenamiento sin fila en `audio_assets` y más antiguos que un margen (una hora), para no tocar una carga en curso.
- **Resultados tardíos:** `JobStore.complete` y `advance` solo actúan si el trabajo sigue en curso; si `maintenance` lo dejó en `expired`, el worker descarta el resultado y lo registra (ADR-0002). El worker no reclama trabajos `expired`.
- **Bloqueo:** un audio vencido no se procesa aunque su archivo siga en disco por un borrado fallido: la comprobación es por `expires_at`, no por la existencia del archivo.
- Los trabajos terminados (`ready_for_review`) conservan su resultado; solo se purga el audio.

### Contrato v0.2

Sube MINOR, porque solo añade ([CONTRACTS](../../../docs/CONTRACTS/README.md)):

- `ErrorCode.invalid_audio_duration` (422).
- La ficha documenta los formatos admitidos, que los límites son configurables con sus valores por defecto, el orden de los errores y que `expired` ya se produce.
- `JobState.expired` ya está declarado; el trabajo caducado no lleva `error`.
- La web regenera sus tipos desde `backend/openapi.json`.

### Web

La subida acepta en el selector los formatos del contrato, muestra un mensaje claro para 413, 415 e `invalid_audio_duration`, y el progreso muestra el estado `expired`. No valida la duración en el navegador: la API es la que decide.

## Risks / Trade-offs

- **Dependencia de #38:** las specs `class-processing` y `api-access` llegan a `openspec/specs/` con su archive, así que este cambio se archiva después. La sección de integración depende de que #38 esté en `dev` porque toca los mismos archivos de Compose. Las secciones de contrato, backend y web no tocan Compose y pueden avanzar antes.
- **`ffprobe` en local sin Docker:** quien ejecute los tests sin FFmpeg no verá los de validación; `make ci` los ejecuta siempre.
- **Uploads grandes en memoria:** se escribe a disco por bloques para no cargar 150 MB en memoria.
- **Purga con precisión de minutos:** depende del intervalo de `maintenance`; si está parado, el audio vencido se bloquea igual (por `expires_at`) y se borra al arrancar.

## Migration Plan

Migración de Alembic que añade `audio_assets` y la clave de idempotencia a `classes`. Las clases de prueba creadas con el skeleton no tienen audio: la migración no las toca y `maintenance` las ignora.

## Open Questions

- Conservación de transcripciones y resultados tras la purga del audio (PRD §14): fuera de este cambio.
- Verificación real del consentimiento (PRD §14): sigue validándose solo la forma de `consent_reference`.
