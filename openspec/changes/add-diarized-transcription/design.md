# Design

## Context

Ver [proposal.md](proposal.md). El worker del walking skeleton ([add-walking-skeleton](../add-walking-skeleton/design.md)) recorre las etapas con `FakePipeline` y pasa siempre `audio_path=None`. Desde #46 ([add-class-reception](../add-class-reception/design.md)) el audio de cada clase se guarda validado tras `AudioStorage`, con su fila en `audio_assets`. Mientras se planifica:

- #47 está pendiente: purga, caducidad de los trabajos y que `complete` y `advance` solo actúen sobre trabajos en curso. Cambia la `JobStore` y el worker, igual que los reintentos de este cambio.
- #38 y #49 añaden a Compose el worker, `maintenance` y el volumen del audio. Hasta entonces `make up` no levanta el worker.
- Existe un borrador anterior, `add-speaker-diarization` (rama `docs/E3-add-speaker-diarization`, sin PR), y el PR #52 con un adaptador de diarización (pyannote 3.1 con un fallback de librosa y scikit-learn) y un `RealPipeline` que sustituye a `FakePipeline` en el worker con un texto fijo en los segmentos. Este cambio sustituye ese borrador; el adaptador y sus tests son el punto de partida de la sección 3.

## Goals / Non-Goals

**Goals:**

- Procesar el audio guardado de cada clase con modelos reales y producir la transcripción diarizada del contrato.
- Adaptadores intercambiables por etapa, probados en el CI con dobles y sin descargar modelos.
- Reintentar solos los fallos transitorios, con un límite, sin que un trabajo bloquee la cola.
- Medir el tiempo y la memoria de cada etapa en el equipo de la demo y documentarlos (RNF-04).

**Non-Goals:** el análisis pedagógico (E4), que de momento sale vacío; asociar personas hablantes a participantes y corregir la transcripción (E5); marcar los solapamientos en el contrato; reanudar un reintento desde la etapa que falló; la GPU; fijar umbrales de calidad, que siguen abiertos en el PRD §14.

## Decisions

### Etapas y adaptadores

`StagedPipeline`, en `app/inference/`, implementa el `InferencePipeline` existente y ejecuta un adaptador por etapa de `JobStage`. Cada adaptador carga su modelo al empezar su etapa y lo libera al terminar, para no tener varios modelos en memoria a la vez (ARCHITECTURE §7). `FakePipeline` se mantiene para los tests y para trabajar sin modelos.

| Etapa | Interfaz | Adaptador real | Entrada → salida |
|---|---|---|---|
| `normalizing` | `Normalizer` | FFmpeg | audio guardado → WAV PCM de 16 kHz y un canal en el directorio de trabajo del trabajo |
| `transcribing` | `Transcriber` | faster-whisper | WAV → frases reconocidas, con sus palabras y sus marcas en milisegundos |
| `diarizing` | `Diarizer` | pyannote.audio | WAV y máximo de voces → turnos de habla sin solapamiento, uno por voz y tramo |
| `diarizing` | `assign_speakers` (función, sin modelo) | — | frases y turnos → `Transcript` del contrato |
| `analyzing` | `Analyzer` | vacío hasta E4 | `Transcript` → `Analysis` sin elementos y con resumen vacío |

El worker elige el pipeline con `INFERENCE_PIPELINE` (`models` o `fake`). La sección 1 crea `StagedPipeline` y lo prueba con adaptadores falsos; las secciones 2 y 3 añaden los adaptadores reales, y la 6 los conecta en la entrada del worker.

### Combinación de palabras y personas hablantes

`assign_speakers` es una función pura, probada sin modelos:

1. Cada palabra reconocida toma la voz del turno con el que más se solapa. Si no se solapa con ninguno, toma la del turno más cercano a menos de un segundo; si no hay ninguno tan cerca, la de la palabra anterior de su frase. Si la diarización no devuelve turnos pero hay palabras, todo es de una sola voz.
2. Dentro de cada frase, las palabras seguidas de la misma voz forman un segmento: un cambio de voz parte la frase.
3. Las voces se declaran en el orden de su primer segmento (`speaker-1`, `speaker-2`…) y los segmentos se numeran en orden temporal (`segment-1`…). Solo se declaran las voces que tienen algún segmento.
4. `participant_id` siempre es nulo: los nombres de los participantes no identifican voces (RD-04, ARCHITECTURE §5).
5. Los tiempos son milisegundos enteros y cada segmento acaba al menos 1 ms después de empezar, como exige el contrato.

**Solapamientos:** la diarización exclusiva de Community-1 asigna cada instante a una sola voz, así que el texto dicho a la vez se atribuye a la voz dominante y no se marca. Queda como limitación documentada en la ficha del contrato y en ARCHITECTURE §5, que hoy dice que los solapamientos «quedan señalados». Alternativa descartada para el 11 de diciembre: un campo opcional en `Segment` (contrato 0.3.0), que obligaría a la web a esperar a una sección de contrato. Se puede añadir después como cambio MINOR.

**Participantes:** el número de participantes de la clase se pasa como máximo de voces (`max_speakers`), nunca como número exacto, para que un participante en silencio no fuerce una voz más.

### Normalización

FFmpeg lee solo el archivo local con los demuxers que admite la recepción (E2) y escribe un WAV PCM de 16 kHz y un canal. Cambiar la frecuencia y los canales no desplaza los tiempos, así que las marcas siguen siendo las de la grabación original. Un audio que FFmpeg no puede decodificar falla con `invalid_audio`, sin reintento.

### Transcripción

faster-whisper con Whisper `small` multilingüe (ADR-0003), en CPU con `int8`, marcas por palabra y filtro de actividad de voz para no transcribir los silencios. Variables: `ASR_MODEL` (`small`), `ASR_DEVICE` (`cpu`), `ASR_COMPUTE_TYPE` (`int8`) y `ASR_LANGUAGE` (vacía: el idioma se detecta). Las clases de idiomas mezclan lengua vehicular y lengua meta: la medición comprueba también la detección de idioma por frase de faster-whisper (`multilingual`) y decide el valor por defecto.

`make -C backend measure` mide normalizar y transcribir juntos con `ASR_MEASURE_AUDIO` (WAV mono de 16 kHz). `ASR_REFERENCE` aporta el texto esperado en JSON `{"text": "..."}` para calcular el WER, y `ASR_MULTILINGUAL_SAMPLE` permite comparar la detección de idioma por frase con la del archivo completo. Ninguna medición usa datos de clase: las muestras son sintéticas.

### Diarización

pyannote.audio 4 con `pyannote/speaker-diarization-community-1` (ADR-0003), en CPU, usando su salida exclusiva, pensada para cruzarla con las marcas de la transcripción. El adaptador le pasa el audio ya cargado del WAV normalizado, sin depender de los decodificadores de cada plataforma.

- **Pesos con condiciones:** Community-1 (CC-BY-4.0) pide aceptar sus condiciones en Hugging Face y un token para descargarlo. El token va en el `.env` de quien descarga, nunca en Git ni en la imagen.
- **Sin fallback silencioso:** se descarta el fallback de librosa y scikit-learn de #52. Agrupa siempre en un número fijo de voces, lo que contradice el escenario «Participante en silencio», y cambiar de modelo sin avisar va contra ARCHITECTURE §5. Si el modelo no está, el trabajo falla con `processing_unavailable` y sigue los reintentos.
- **Community-1 en lugar de 3.1:** es el modelo de ADR-0003 y trae la salida exclusiva.

### Modelos y descarga

- Los pesos viven en una caché privada, `MODELS_DIR`: un volumen en Compose, fuera de Git y de las copias de seguridad.
- La descarga va separada del procesamiento (ARCHITECTURE §6): `make -C backend models` descarga las revisiones fijadas de cada modelo. El worker trabaja sin red hacia Hugging Face (`HF_HUB_OFFLINE=1`) y, si falta un modelo, la etapa falla con `processing_unavailable` (spec `diarized-transcription`, «Modelos preparados antes de procesar»).
- Al arrancar, el worker registra el modelo, la revisión, el dispositivo y el tipo de cálculo de cada etapa (ADR-0003), sin datos de clases.

### Medición de la diarización

`make -C backend measure` solo mide diarización cuando se configura `DIARIZATION_MEASURE_AUDIO` con un WAV mono de 16 kHz; sin esa variable informa de que no hay audio configurado. Devuelve segundos por minuto de audio, pico de memoria y número de turnos. Si se configura `DIARIZATION_REFERENCE`, calcula también el DER contra un JSON de turnos esperados con el formato `{"turns": [{"start_s": 0, "end_s": 1, "speaker": "A"}]}`. `DIARIZATION_MAX_SPEAKERS` fija el máximo de voces de la medición. Ninguna medición incluye datos de clase: el audio y la referencia son sintéticos.

### Dependencias e imagen del worker

- Las dependencias de inferencia (faster-whisper, pyannote.audio y PyTorch para CPU) van en `backend/requirements-inference.txt`, aparte de `requirements.txt`, para que la API y `maintenance` sigan ligeras.
- El `Dockerfile` de `backend` gana un objetivo `worker` que añade esas dependencias, y el servicio `worker` de Compose lo usa. La API y `maintenance` siguen con la imagen de `backend`. El paquete de dominio es el mismo (ADR-0001).
- Los tests del CI corren en la imagen `dev`, sin dependencias de inferencia: los adaptadores importan sus librerías al cargar el modelo y sus tests usan dobles. Los tests con modelos reales se marcan y solo corren donde están descargados, con `make -C backend test-models`.

### Pipeline en el worker

- El worker resuelve el audio de la clase con `JobStore.get_audio` y `AudioStorage.path` y lo pasa en `PipelineInput.audio_path`. Si el archivo no existe aunque no haya caducado, el trabajo falla con `processing_failed`.
- Cada intento trabaja en `<WORK_DIR>/<job_id>/`, privado, que se borra al terminar el intento, bien o mal. Al arrancar, el worker vacía `WORK_DIR` antes de reclamar nada (un solo worker, ADR-0002). `WORK_DIR` (por defecto `data/work`) está fuera de `AUDIO_STORAGE_DIR`, para que la limpieza de huérfanos de E2 no lo toque.
- Hasta E4, el análisis sale vacío (`general_summary` vacío y sin elementos), en lugar del ejemplo sintético: el resultado no muestra un repaso que no corresponde a la clase. La etapa `analyzing` se sigue recorriendo.

### Reintentos

- **Clasificación:** los adaptadores lanzan `PipelineError` con su código y si es reintentable.
  - `processing_unavailable`, reintentable: modelo ausente o que no carga, memoria agotada, dispositivo no disponible.
  - `invalid_audio`, no reintentable: FFmpeg no puede decodificar el audio.
  - `processing_failed`, no reintentable: una salida que no cumple el contrato o un error inesperado. Un error inesperado suele ser un fallo del código y reintentarlo repetiría todo el procesamiento para nada.
- **`JobStore`:** `retry_later` deja un trabajo en curso en `retry_wait`, con su etapa, su error y la hora del siguiente intento; `claim_next` también reclama los trabajos en `retry_wait` cuya hora ha pasado, por orden de llegada a la cola. Una migración añade `next_attempt_at` a `jobs`.
- **Política:** cada reclamación suma un intento, como ya ocurre. Ante un error reintentable con `attempt` menor que `MAX_ATTEMPTS`, el trabajo pasa a `retry_wait` y espera `RETRY_DELAY_SECONDS × 2^(attempt − 1)`: con los valores por defecto, 1 minuto y después 2. En el último intento pasa a `failed` con el mismo código y `retryable` falso.
- **Al arrancar:** `requeue_in_progress` devuelve a la cola los trabajos a medias que tienen intentos y deja en `failed` con `processing_failed` los que los han agotado, como uno que tumba el worker por memoria en cada intento.
- **Desde el principio:** cada intento empieza en `normalizing`. No se guardan resultados de etapa entre intentos, así que no hay transcripciones fuera del resultado. Reanudar desde la última etapa válida con resultados por etapa (ARCHITECTURE §5) queda como evolución si la medición muestra reprocesados largos.
- **Caducidad:** los trabajos en `retry_wait` también caducan cuando vence su audio (spec `audio-retention`) y no se reclaman. Se apoya en lo que añade #47.
- **Base de datos caída:** sigue como hasta ahora: el trabajo vuelve a la cola sin contar como fallo del trabajo.
- Variables: `MAX_ATTEMPTS` (3) y `RETRY_DELAY_SECONDS` (60).

### Contrato

No cambia ningún campo: sigue en 0.2.0 y `backend/openapi.json` no cambia. La ficha documenta:

- Sección 1: las personas hablantes se declaran en el orden de su primera intervención, con `participant_id` nulo hasta que la docente las asigne (E5); los segmentos van en orden temporal y no se solapan; el texto dicho a la vez se atribuye a una sola voz; una clase sin voz tiene la transcripción vacía; el análisis sale vacío hasta E4.
- Sección 4: `retry_wait` ya se produce; en ese estado `error.retryable` es verdadero y en `failed`, falso; `attempt` cuenta los intentos.

Alternativa descartada: subir a 0.3.0 solo por estas aclaraciones. Los tipos de la web no cambian; la versión subirá cuando E4 o E5 añadan campos.

### Web

- La transcripción se agrupa por persona hablante, con la etiqueta «Hablante N» según su posición en `speakers` (los identificadores son opacos y la web no los interpreta) y la marca de cada intervención en `mm:ss` (`h:mm:ss` a partir de una hora). Los segmentos seguidos de la misma voz se muestran juntos.
- Mensajes para una transcripción sin voz y para un análisis todavía vacío.
- El progreso muestra `retry_wait` con el intento y el mensaje del error, y `failed` con su mensaje.
- Los mocks de MSW añaden un resultado con varias personas hablantes y un trabajo en `retry_wait`. Asignar nombres a las voces es de E5.

### Medición (RNF-04)

`make -C backend measure` ejecuta los adaptadores reales sobre audios locales que no se versionan (grabaciones autorizadas o simuladas) y da, por etapa, los segundos de cálculo por minuto de audio, el pico de memoria y el modelo usado, y el WER y el DER si se le pasa una referencia anotada. La sección 6 añade `make measure-stages AUDIO=<archivo>`, que ejecuta cada etapa en su propio proceso dentro de la imagen del worker para que el pico de memoria sea el de esa etapa; es la que dio los números de ARCHITECTURE §7. Los resultados, sin audio ni texto de las clases, van a ARCHITECTURE §2 y §7. No hay umbral de aceptación (PRD §14): el equipo decide con los números.

### Interfaces internas

- `InferencePipeline` no cambia; `StagedPipeline` lo implementa.
- `Normalizer`, `Transcriber`, `Diarizer` y `Analyzer`, con sus tipos de datos, los declara la sección 1. No van a `docs/CONTRACTS/`: viven en el mismo paquete.
- `JobStore` añade `retry_later`, la hora en `claim_next` y el máximo de intentos en `requeue_in_progress` (sección 4), en memoria y en PostgreSQL.

## Risks / Trade-offs

- **Calidad sin umbral** → se mide y se documenta; el equipo decide con los números y lo explica en la demo (PRD §12).
- **Lentitud en CPU** → una clase de 60 minutos puede tardar decenas de minutos (estimación sin medir). La sección 6 lo mide en el equipo de la demo; la GPU queda como opción posterior, que en Windows exige Docker con WSL2 (ARCHITECTURE §7).
- **Imagen pesada** → PyTorch y sus dependencias hacen la imagen del worker grande y `make ci` más lento. Se limita con PyTorch para CPU y con un objetivo propio que la API no usa.
- **Idiomas** → catalán, chino y los cambios de idioma son riesgos conocidos (ADR-0003); la medición los cubre si hay muestras.
- **Acceso a Community-1** → sin cuenta ni token no se descarga. La sección 6 documenta los pasos; mientras, `INFERENCE_PIPELINE=fake`.
- **Solapamientos sin marcar** → limitación documentada; la docente corrige en E5.
- **Reintentos desde el principio** → un fallo tardío repite todo el procesamiento, acotado por `MAX_ATTEMPTS` y solo para errores transitorios.
- **Trabajo en paralelo sobre `backend/`** → la sección 1 fija las interfaces; las secciones 2 y 3 solo añaden módulos de adaptadores, y la 4 toca la `JobStore` y el worker después de la 1 y de #47.
- **Dependencias de #38, #47 y #49** → la sección 4 espera a #47; la 6 espera a #49, que toca los mismos archivos de Compose; el archive va después de los de `add-walking-skeleton` y `add-class-reception`.

## Migration Plan

- Migración de Alembic que añade `next_attempt_at` (nullable) a `jobs`. Los trabajos existentes no cambian.
- Antes de procesar con modelos, `make -C backend models` descarga los pesos. Sin ellos, los trabajos acaban en `failed` con `processing_unavailable`; para trabajar sin modelos, `INFERENCE_PIPELINE=fake`.

## Open Questions

- Idiomas de la demo y umbrales de WER y DER (PRD §14): no cambian el plan; la medición da los números.
- Detección de idioma por frase (`multilingual`): la sección 6 midió solo recursos, sin muestra multilingüe de referencia, así que queda aplazada como pregunta abierta en ARCHITECTURE §11; mientras, `ASR_LANGUAGE` vacía detecta el idioma.
- Equipo de la demo y su GPU (ARCHITECTURE §11): el plan funciona en CPU; si el equipo tiene una GPU NVIDIA usable desde Docker, añadirla es una mejora posterior.
