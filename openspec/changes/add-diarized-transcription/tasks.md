# Tasks

Plan de la funcionalidad `add-diarized-transcription` (E3, épica #3). Una sección por historia: primero el pipeline por etapas con sus interfaces, que desbloquea los adaptadores y los reintentos; después una sección por capa, que pueden avanzar en paralelo, y la integración al final. La web no depende de ninguna porque el contrato no cambia de campos. El diseño está en [design.md](design.md).

## 1. Pipeline por etapas con adaptadores (backend) · #55

**Criterios de aceptación:**
- `StagedPipeline` implementa `InferencePipeline` con las interfaces `Normalizer`, `Transcriber`, `Diarizer` y `Analyzer` del diseño y, con adaptadores falsos, produce una transcripción que cumple el contrato y la spec `diarized-transcription`, «Intervenciones por persona hablante» y «Transcripción con marcas temporales» (RF-02, RD-04).
- El número de participantes llega al diarizador como máximo de voces y el análisis sale vacío hasta E4.
- El worker procesa el audio guardado de la clase y sus copias de trabajo cumplen la spec `diarized-transcription`, «Copias de trabajo efímeras» (RNF-01, RNF-02).
- Quedan preparados `requirements-inference.txt`, el marcador de tests con modelos y los objetivos `models`, `test-models` y `measure` de `backend/Makefile`, para que las secciones 2 y 3 solo añadan su adaptador.
- La ficha del contrato documenta cómo se producen las personas hablantes y los segmentos; `backend/openapi.json` no cambia.
- `make backend-test` y `make backend-lint` pasan.

**Depende de:** —

- [ ] 1.1 Declarar en `app/inference/` los tipos de frases, palabras y turnos, las interfaces `Normalizer`, `Transcriber`, `Diarizer` y `Analyzer`, y el analizador vacío, con tests de sus invariantes.
- [ ] 1.2 Implementar `assign_speakers` con las reglas del diseño, con un test por escenario de «Intervenciones por persona hablante» y el de «Audio sin voz».
- [ ] 1.3 Implementar `StagedPipeline`: avisa de cada etapa, carga y libera el modelo de cada adaptador, pasa el máximo de voces y propaga `PipelineError`; tests con adaptadores falsos y la salida validada contra el contrato.
- [ ] 1.4 Pasar al pipeline la ruta del audio guardado (`JobStore.get_audio` y `AudioStorage.path`), con `processing_failed` si el archivo falta sin haber caducado; tests del worker.
- [ ] 1.5 Añadir `WORK_DIR` a `Settings`: un directorio privado por intento que se borra al terminar, bien o mal, y que el worker vacía al arrancar; tests de los dos escenarios de «Copias de trabajo efímeras».
- [ ] 1.6 Crear `backend/requirements-inference.txt`, el marcador de pytest de los tests con modelos y los objetivos `models`, `test-models` y `measure`, con un registro al que cada adaptador añade su descarga y su medición; comprobar que `make backend-test` no los ejecuta.
- [ ] 1.7 Actualizar la ficha del contrato (skill `contracts`, sin cambiar la versión), ARCHITECTURE §4 (`app/inference/`) y §5 (combinación, solapamientos y copias de trabajo) y `backend/.env.example` (`WORK_DIR`).

## 2. Normalización y transcripción con faster-whisper (inferencia) · #56

**Criterios de aceptación:**
- La normalización deja un WAV de 16 kHz y un canal en el directorio de trabajo; un audio que FFmpeg no puede decodificar falla con `invalid_audio`, sin reintento.
- La transcripción con faster-whisper (Whisper `small`, CPU, `int8`) devuelve frases con sus palabras y marcas en milisegundos desde el principio de la grabación original (RF-02).
- El modelo se carga de `MODELS_DIR` sin descargar nada; si falta, no carga o se agota la memoria, la etapa falla con `processing_unavailable` reintentable (spec `diarized-transcription`, «Modelos preparados antes de procesar»).
- `make -C backend models` descarga la revisión fijada del modelo; `make -C backend measure` da los segundos por minuto de audio y el pico de memoria de normalizar y transcribir, y el WER si recibe una referencia (RNF-04).
- Los tests con dobles pasan en `make backend-test` y los marcados pasan con `make -C backend test-models` donde el modelo está descargado.

**Depende de:** 1

- [ ] 2.1 Implementar el normalizador con FFmpeg, limitado a archivos locales y a los formatos de la recepción, con tests sobre audios sintéticos generados al ejecutarse.
- [ ] 2.2 Fijar faster-whisper en `requirements-inference.txt` e implementar el transcriptor (importación al cargar, marcas por palabra, filtro de voz, `ASR_MODEL`, `ASR_DEVICE`, `ASR_COMPUTE_TYPE` y `ASR_LANGUAGE`), con tests con dobles que cubren la traducción de errores.
- [ ] 2.3 Registrar la descarga de la revisión fijada en `models` y un test marcado con el modelo real sobre un audio con voz sintética generada al ejecutarse.
- [ ] 2.4 Registrar la medición de normalizar y transcribir en `measure`, con WER si hay referencia, y comparar con una muestra que mezcle idiomas la detección por frase (`multilingual`) con la detección única; anotar el resultado en el PR.
- [ ] 2.5 Añadir las variables `ASR_*` y `MODELS_DIR` a `Settings` y a `backend/.env.example`.

## 3. Diarización con pyannote (inferencia) · #57

**Criterios de aceptación:**
- El diarizador usa `pyannote/speaker-diarization-community-1` en CPU y devuelve su diarización exclusiva en turnos con marcas en milisegundos, con el número de participantes como máximo de voces (RF-02, RD-04).
- No hay fallback a otro modelo: si el modelo falta, no carga o se agota la memoria, la etapa falla con `processing_unavailable` reintentable (spec `diarized-transcription`, «Modelos preparados antes de procesar»).
- `make -C backend models` descarga la revisión fijada con el token de Hugging Face del `.env`, que no se versiona ni aparece en los logs.
- `make -C backend measure` da los segundos por minuto de audio y el pico de memoria de la diarización, y el DER si recibe una referencia (RNF-04).
- Los tests con dobles pasan en `make backend-test` y los marcados pasan con `make -C backend test-models` donde el modelo está descargado.

**Depende de:** 1

- [ ] 3.1 Adaptar el diarizador del PR #52 a la interfaz `Diarizer`: Community-1, salida exclusiva, audio cargado del WAV normalizado y máximo de voces; quitar el fallback, `RealPipeline` y el cambio del worker; tests con dobles que cubren la traducción de errores.
- [ ] 3.2 Fijar pyannote.audio y PyTorch para CPU en `requirements-inference.txt`, en versiones compatibles con faster-whisper, y comprobar que se instalan juntos.
- [ ] 3.3 Registrar la descarga de Community-1 en `models` con `HF_TOKEN` y añadir `HF_TOKEN` vacío y comentado a `backend/.env.example`.
- [ ] 3.4 Registrar la medición de la diarización en `measure`, con DER si hay referencia, y un test marcado con el modelo real sobre un audio sintético de dos voces generado al ejecutarse.

## 4. Reintentos automáticos de los trabajos (backend) · #58

**Criterios de aceptación:**
- El worker cumple la spec `class-processing`, «Seguimiento del trabajo por etapas»: un fallo transitorio deja el trabajo en `retry_wait` con su etapa y un error reintentable, y se reintenta tras `RETRY_DELAY_SECONDS × 2^(attempt − 1)`; el último intento o un fallo que no es transitorio lo dejan en `failed` (RNF-05, ADR-0002).
- Al arrancar, el worker devuelve a la cola los trabajos a medias con intentos y deja en `failed` los que los han agotado.
- Los trabajos en `retry_wait` caducan cuando vence su audio y no se reclaman (spec `audio-retention`, «Trabajos caducados»).
- `MAX_ATTEMPTS` (3) y `RETRY_DELAY_SECONDS` (60) se configuran por entorno.
- Los tests con la `JobStore` en memoria y en PostgreSQL y un reloj simulado pasan en `make ci`; los logs llevan el trabajo, la etapa, el intento, el código de error y la espera, sin datos de la clase.

**Depende de:** 1 y la purga del audio (#47)

- [ ] 4.1 Migración de Alembic con `next_attempt_at` en `jobs`; `retry_later` y la hora en `claim_next` en las dos `JobStore`, con tests.
- [ ] 4.2 Aplicar en el worker la política de reintentos del diseño con un reloj inyectable, con un test por escenario de la spec.
- [ ] 4.3 Pasar el máximo de intentos a `requeue_in_progress` y dejar en `failed` los trabajos agotados al arrancar, con tests.
- [ ] 4.4 Incluir los trabajos en `retry_wait` en la caducidad de #47, con tests con un plazo vencido.
- [ ] 4.5 Añadir `MAX_ATTEMPTS` y `RETRY_DELAY_SECONDS` a `Settings` y a `backend/.env.example`, documentar `retry_wait` en la ficha del contrato (sin cambiar la versión) y marcar como Actual lo que corresponda de ARCHITECTURE §5, «Fallos y recuperación».

## 5. Transcripción por hablante en la web (frontend) · #59

**Criterios de aceptación:**
- El resultado muestra la transcripción agrupada por persona hablante, con la etiqueta «Hablante N» según su posición en `speakers` y la marca de cada intervención en `mm:ss` (RF-02, RF-04).
- Hay mensajes claros para una transcripción sin voz y para un análisis todavía vacío.
- El progreso muestra `retry_wait` con el intento y el mensaje del error, y `failed` con su mensaje.
- Los mocks cubren un resultado con varias personas hablantes y un trabajo en `retry_wait`; `make frontend-test` y `make frontend-lint` pasan.

**Depende de:** —

- [x] 5.1 Mostrar la transcripción por persona hablante, con las intervenciones seguidas de la misma voz juntas y las marcas en `mm:ss` (`h:mm:ss` desde una hora), con tests de componentes.
- [x] 5.2 Mostrar los mensajes de transcripción sin voz y de análisis vacío, con tests.
- [x] 5.3 Mostrar `retry_wait` y `failed` en el progreso del trabajo, con tests.
- [x] 5.4 Añadir a los mocks de MSW un resultado con varias personas hablantes, uno sin voz y un trabajo en `retry_wait`, sin datos reales.

## 6. Transcripción diarizada de extremo a extremo en local (integración) · #60

**Criterios de aceptación:**
- Con #49 en `dev`, `make up` y `make up-prod` levantan el worker con el objetivo `worker` de la imagen, `INFERENCE_PIPELINE=models`, la caché de modelos y el volumen del audio; la API y `maintenance` siguen con la imagen de `backend`.
- Con los modelos descargados, un audio con voz sintética de dos voces subido desde la web, sin mocks, termina con su transcripción por persona hablante; sin modelos, el trabajo agota sus intentos y termina en `failed` con `processing_unavailable`.
- La prueba E2E de `make e2e` cubre esa subida hasta la transcripción diarizada.
- Medido en el equipo de la demo con grabaciones autorizadas o simuladas de 30 y 60 minutos: segundos por minuto de audio y pico de memoria de cada etapa, documentados en ARCHITECTURE sin datos de las clases (RNF-04).
- `make ci` pasa, también con la imagen del worker, y `verify` del cambio no deja discrepancias con las specs.

**Depende de:** 1, 2, 3, 4, 5 y la recepción de extremo a extremo (#49)

- [ ] 6.1 Añadir el objetivo `worker` (desarrollo y producción) al `Dockerfile` de `backend` con `requirements-inference.txt`, y en los tres archivos de Compose el servicio `worker` con ese objetivo, el volumen privado de `MODELS_DIR`, `INFERENCE_PIPELINE` y `HF_HUB_OFFLINE`.
- [ ] 6.2 Conectar en la entrada del worker `StagedPipeline` con los adaptadores reales según `INFERENCE_PIPELINE` y registrar al arrancar el modelo, la revisión y el dispositivo de cada etapa.
- [ ] 6.3 Ampliar la prueba E2E con un audio de dos voces sintéticas generado al ejecutarse y comprobar la transcripción por persona hablante en la web.
- [ ] 6.4 Medir con grabaciones de 30 y 60 minutos y actualizar ARCHITECTURE §2 (modelos), §3 (imagen del worker), §6 (caché de modelos y token), §7 (recursos medidos) y §11 (hardware y modelos).
- [ ] 6.5 Explicar en el README cómo aceptar las condiciones de Community-1, descargar los modelos, levantar la demo y trabajar sin modelos (`INFERENCE_PIPELINE=fake`).
- [ ] 6.6 Ejecutar `verify`, `sync` y `archive` del cambio (skill `pull-requests`), después del archive de `add-class-reception`.
