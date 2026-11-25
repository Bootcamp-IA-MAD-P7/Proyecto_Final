# Spec Delta

## Purpose

Que el sistema produzca una transcripción diarizada: detectar cuántas personas hablan en una grabación, separar sus intervenciones con marcas temporales y asociar cada segmento a un `speaker_id` de sesión, sin equiparar el número de voces con el número de participantes ni inferir nombres por orden. El comportamiento se integra en la etapa `DIARIZING` del lifecycle de trabajo existente. El contrato está en [CONTRACTS](../../../../../docs/CONTRACTS/README.md).

## ADDED Requirements

### Requirement: Diarización de una sesión de clase
La etapa de procesamiento SHALL ejecutar diarización sobre el audio de una clase, SHALL devolver uno o más `speaker_id` de sesión con sus intervalos de intervención y SHALL incluirlos en la `Transcript` del resultado, con `start_ms` y `end_ms` enteros no negativos, `end_ms > start_ms` y `speaker_id` declarado en `speakers` (RF-02).

#### Scenario: Dos hablantes en audio corto
- **WHEN** se diariza un archivo de audio corto con dos personas hablando por turnos
- **THEN** se detectan exactamente dos `speaker_id` distintos y cada segmento tiene un `speaker_id` de esos dos.

#### Scenario: Participante en silencio
- **WHEN** un participante de la clase permanece en silencio durante toda la sesión
- **THEN** no se le asigna un `speaker_id` por su sola presencia en la lista de participantes; solo se detectan las voces que efectivamente hablan.

#### Scenario: Solapamiento o asociación dudosa
- **WHEN** hay solapamiento de voces o una atribución ambigua entre hablantes
- **THEN** el resultado no inventa identidad de hablante, admite `participant_id` nulo en `Speaker` y deja la corrección manual para la historia de edición de asociaciones (017).

### Requirement: Representación de la ambigüedad
La `Transcript` SHALL permitir `speaker_id` sin `participant_id` asignado (nullable), y el resultado SHALL conservar el `speaker_id` de sesión incluso cuando no se pueda asociar a un participante (RD-04).

#### Scenario: Sin asignación de participante
- **WHEN** un `speaker_id` detectado no se puede asociar con ningún `participant_id` de la clase
- **THEN** el `Speaker` correspondiente tiene `participant_id: null` y la transcripción sigue siendo válida y consultable.
