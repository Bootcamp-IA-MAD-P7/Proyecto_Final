# Tasks

Plan de la funcionalidad `add-class-reception` (E2, épica #2). Una sección por historia: el contrato primero, después una sección por capa, que pueden avanzar en paralelo, y la integración al final. El diseño está en [design.md](design.md).

## 1. Contrato v0.2 de recepción (contrato) · #45

**Criterios de aceptación:**
- `backend/openapi.json` (0.2.0) incluye `invalid_audio_duration` en los errores de `POST /v1/classes`, y el test de desviación pasa.
- `docs/CONTRACTS/coteach-ai-api.md` (0.2.0) documenta los formatos admitidos, los límites configurables con sus valores por defecto, el orden de los errores de la recepción y que `expired` ya se produce, sin copiar campos.
- Los fixtures del contrato tienen los ejemplos de los errores nuevos de la recepción.
- `make backend-test` y `make backend-lint` pasan.

**Depende de:** —

- [x] 1.1 Añadir `ErrorCode.INVALID_AUDIO_DURATION` con su mensaje seguro y declararlo en la respuesta 422 de `POST /v1/classes`.
- [x] 1.2 Subir la versión del contrato a 0.2.0 y regenerar `backend/openapi.json` con `make -C backend openapi`.
- [x] 1.3 Añadir a `backend/tests/fixtures/contract/` los ejemplos de error de 413, 415 e `invalid_audio_duration`.
- [x] 1.4 Actualizar la ficha del contrato (skill `contracts`): formatos, límites, orden de errores, `expired` y la nota de compatibilidad MINOR.

## 2. Recepción y almacenamiento del audio (backend) · #46

**Criterios de aceptación:**
- `POST /v1/classes` guarda el audio validado en el almacenamiento privado y crea clase, audio y trabajo en una transacción antes de responder 202 (spec `class-processing`, «Envío de una clase»).
- Un audio de más de `UPLOAD_MAX_BYTES` recibe 413, uno que no es Opus, MP3 o AAC por su contenido recibe 415 y uno fuera de `UPLOAD_MIN_SECONDS`–`UPLOAD_MAX_SECONDS` recibe 422 `invalid_audio_duration`; en ninguno queda un archivo guardado.
- `Idempotency-Key` cumple la spec `class-processing`, «Recepción idempotente».
- Cada audio registra `received_at` y `expires_at` a `AUDIO_RETENTION_DAYS` (spec `audio-retention`, «Plazo de conservación registrado»).
- La imagen de `backend` incluye FFmpeg; los tests de validación pasan en `make ci`.

**Depende de:** 1

- [x] 2.1 Añadir FFmpeg a la imagen de `backend` y un helper de tests que genere audios sintéticos con `ffmpeg`, que salta los tests con un aviso si no está instalado.
- [x] 2.2 Crear `app/storage/` con `AudioStorage` y su implementación en disco bajo `AUDIO_STORAGE_DIR` (temporal, confirmar con nombre opaco, borrar, listar), con tests.
- [x] 2.3 Validar el audio: copia por bloques con corte a `UPLOAD_MAX_BYTES`, y formato y duración con `ffprobe`, con tests de cada error.
- [x] 2.4 Migración de Alembic con `audio_assets` y la clave y la huella de idempotencia en `classes`; ampliar `JobStore` (memoria y PostgreSQL) para crear clase, audio y trabajo juntos.
- [x] 2.5 Conectar la ruta: orden de errores del diseño, borrar el archivo si la transacción falla, e idempotencia por quien envía y su clave, con tests de los escenarios de la spec.
- [x] 2.6 Añadir `UPLOAD_MAX_BYTES`, `UPLOAD_MIN_SECONDS`, `UPLOAD_MAX_SECONDS`, `AUDIO_RETENTION_DAYS` y `AUDIO_STORAGE_DIR` a `Settings` y a `backend/.env.example`, y ARCHITECTURE §4 (`app/storage/`) y §11 (límites de carga cerrados).

## 3. Purga del audio y trabajos caducados (backend) · #47

**Criterios de aceptación:**
- El ciclo de `maintenance`, también al arrancar, cumple la spec `audio-retention`: caduca los trabajos sin terminar, borra el audio vencido y registra `deleted_at`, reintenta los borrados fallidos y limpia los huérfanos.
- El worker no reclama trabajos `expired` y descarta el resultado de un trabajo que caducó mientras se procesaba.
- Un trabajo en `ready_for_review` conserva su resultado tras la purga.
- Los tests contra PostgreSQL pasan en `make ci`; los logs no llevan rutas, nombres ni datos de la clase.

**Depende de:** 2

- [x] 3.1 Añadir a `JobStore` (memoria y PostgreSQL) caducar los trabajos sin terminar con el audio vencido y listar y marcar los audios por purgar, con tests.
- [x] 3.2 Hacer que `complete` y `advance` solo actúen sobre trabajos en curso, y que el worker descarte y registre el resultado de un trabajo caducado.
- [x] 3.3 Implementar el ciclo de purga en `maintenance`, con la ejecución al arrancar y el reintento de borrados fallidos.
- [x] 3.4 Limpiar los archivos huérfanos más antiguos que el margen del diseño.
- [x] 3.5 Tests de los escenarios de la spec `audio-retention` con un reloj simulado.

## 4. Subida real y estados del audio en la web (frontend) · #48

**Criterios de aceptación:**
- Los tipos del cliente se regeneran del contrato 0.2.0 y `make frontend-lint` pasa.
- El selector de la subida admite los formatos del contrato y la web muestra un mensaje claro para 413, 415 e `invalid_audio_duration`.
- El progreso muestra el estado `expired` con un texto que explica que el audio ya no está disponible.
- Los mocks cubren los errores nuevos y `make frontend-test` pasa.

**Depende de:** 1

- [x] 4.1 Regenerar los tipos desde `backend/openapi.json`.
- [x] 4.2 Limitar el selector a los formatos admitidos y mostrar los mensajes de error de la recepción.
- [x] 4.3 Mostrar el estado `expired` en el progreso del trabajo.
- [x] 4.4 Añadir a los mocks de MSW los errores de la recepción y un trabajo caducado, con sus tests.

## 5. Recepción de extremo a extremo en local (integración) · #49

**Criterios de aceptación:**
- Con #38 en `dev`, `make up` y `make up-prod` montan el volumen privado del audio en `backend`, `worker` y `maintenance`, fuera de Git.
- Desde la web, sin mocks, se sube un audio sintético válido y avanza hasta el resultado; uno no admitido muestra su error.
- La prueba E2E de `make e2e` cubre la subida válida y un error de formato.
- Con un plazo de conservación corto configurado, `maintenance` purga el audio en local y el trabajo sin terminar queda en `expired`.
- `make ci` pasa y `verify` del cambio no deja discrepancias con las specs.

**Depende de:** 1, 2, 3, 4 y la integración del skeleton (#38)

- [x] 5.1 Añadir el volumen del audio y `AUDIO_STORAGE_DIR` a los tres archivos de Compose y a `.env.example`.
- [x] 5.2 Ampliar la prueba E2E con la subida de un audio sintético válido y de uno no admitido.
- [x] 5.3 Comprobar la purga en local con un plazo corto y documentar cómo hacerlo en el README.
- [x] 5.4 Actualizar ARCHITECTURE §7 (volumen del audio) y marcar como Actual lo que corresponda en §3.
- [ ] 5.5 Ejecutar `verify`, `sync` y `archive` del cambio (skill `pull-requests`), después del archive de `add-walking-skeleton`.

## 6. Límite temprano y formatos de recepción (backend/frontend) · #54

**Criterios de aceptación:**
- `POST /v1/classes` rechaza con 413 `audio_too_large` antes de analizar todo el multipart cuando `Content-Length` supera el límite del audio más un margen documentado para metadatos, y corta transmisiones sin cabecera o con valor inferior al cuerpo real.
- El límite exacto de `UPLOAD_MAX_BYTES` se mantiene sobre el archivo, sin dejar temporales, clases, trabajos ni registros residuales al rechazar.
- La autenticación y autorización conservan su prioridad; idempotencia y los demás errores de recepción existentes siguen cubiertos.
- Matroska con Opus y MOV/3GP con AAC se aceptan por contenido; los códecs, contenedores y vídeos no admitidos se rechazan. El selector y mensajes web reflejan exactamente esos formatos.
- La ficha `docs/CONTRACTS/coteach-ai-api.md` describe el comportamiento sin variar la versión 0.2.0 ni el esquema OpenAPI.

**Depende de:** 1 y 2.

- [x] 6.1 Añadir el middleware de límite multipart temprano, con margen documentado, autenticación/autorización previa y respuesta de contrato 413.
- [x] 6.2 Mantener la validación exacta del archivo y cubrir `Content-Length`, transmisión real, interrupción, limpieza y prioridades de error con pruebas de regresión.
- [x] 6.3 Ampliar los audios sintéticos y pruebas de recepción para Matroska/Opus y MOV/3GP/AAC, manteniendo los rechazados.
- [x] 6.4 Actualizar la ficha del contrato y, solo si procede, el selector y mensajes web para los formatos admitidos; ejecutar las validaciones de las capas afectadas.
