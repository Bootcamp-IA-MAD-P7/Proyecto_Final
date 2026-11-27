# diarized-transcription Specification

## Purpose
Que el resultado de cada clase procesada contenga su transcripción diarizada: el texto con marcas temporales y cada intervención atribuida a una persona hablante de la sesión, sin inventar voces ni identidades, y que el procesamiento no deje copias del audio ni lo saque del servicio. El contrato está en [CONTRACTS](../../../docs/CONTRACTS/README.md).

## Requirements

### Requirement: Transcripción con marcas temporales
Al procesar una clase, el servicio SHALL transcribir su audio guardado y SHALL incluir en el resultado los segmentos de texto en orden temporal, cada uno con su inicio y su fin en milisegundos desde el principio de la grabación original (RF-02, RF-04).

#### Scenario: Clase con voz
- **WHEN** termina el procesamiento de una clase en la que se habla
- **THEN** su resultado contiene la transcripción en segmentos ordenados por tiempo, cada uno con su texto, su inicio y su fin.

#### Scenario: Audio sin voz
- **WHEN** el audio de una clase no contiene voz
- **THEN** el trabajo termina en `ready_for_review` con una transcripción sin personas hablantes ni segmentos, sin texto inventado.

### Requirement: Intervenciones por persona hablante
El servicio SHALL atribuir cada segmento a una persona hablante detectada en la sesión, con identificadores propios de la sesión que se declaran en el orden en que cada voz interviene por primera vez. SHALL declarar solo las voces que tienen algún segmento, sin buscar más voces que participantes tiene la clase, y SHALL NOT asociar ninguna voz a un participante: todas quedan con `participant_id` nulo hasta que la docente las asigne (RF-02, RD-04).

#### Scenario: Dos personas por turnos
- **WHEN** termina el procesamiento de una clase 1–1 en la que dos personas hablan por turnos
- **THEN** el resultado declara dos personas hablantes y cada segmento lleva la que habla en ese tramo.

#### Scenario: Cambio de persona dentro de una frase
- **WHEN** una persona deja de hablar y otra empieza dentro de lo que el reconocimiento toma como una sola frase
- **THEN** el texto se divide en segmentos distintos, uno por cada persona.

#### Scenario: Participante en silencio
- **WHEN** en una clase grupal un participante no habla en toda la sesión
- **THEN** el resultado no declara ninguna persona hablante por ese participante.

#### Scenario: Nombres de los participantes
- **WHEN** el envío de la clase incluye los participantes con sus nombres
- **THEN** ninguna persona hablante se asocia a un participante por orden, por rol ni por nombre, y todas tienen `participant_id` nulo.

#### Scenario: Voces simultáneas
- **WHEN** dos personas hablan a la vez
- **THEN** cada tramo de texto se atribuye a una sola de las voces detectadas, sin crear una persona hablante nueva para el solapamiento.

### Requirement: Copias de trabajo efímeras
Las copias del audio que necesita el procesamiento SHALL guardarse de forma privada solo mientras se procesa el trabajo: SHALL borrarse cuando el intento termina, bien o mal, y las que deje un worker caído SHALL borrarse cuando vuelve a arrancar (RNF-01, RNF-02).

#### Scenario: Intento terminado
- **WHEN** un intento de procesar un trabajo termina y el trabajo pasa a `ready_for_review`, `retry_wait` o `failed`
- **THEN** no queda ninguna copia de trabajo de su audio.

#### Scenario: Worker caído a mitad de un trabajo
- **WHEN** el worker vuelve a arrancar tras caerse mientras procesaba un trabajo
- **THEN** borra las copias de trabajo que quedaron antes de reclamar otro trabajo.

### Requirement: Modelos preparados antes de procesar
El procesamiento SHALL usar modelos ya descargados y SHALL NOT descargar nada ni enviar el audio fuera del servicio mientras procesa una clase. Si un modelo no está disponible, la etapa SHALL fallar con un error transitorio del contrato, sin producir ningún resultado (RNF-01, RNF-03).

#### Scenario: Modelo no disponible
- **WHEN** se procesa una clase y uno de los modelos no está descargado o no se puede cargar
- **THEN** la etapa falla con `processing_unavailable` y el trabajo sigue la política de reintentos, sin descargar el modelo ni producir un resultado.
