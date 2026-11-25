# Spec Delta

## MODIFIED Requirements

### Requirement: Seguimiento del trabajo por etapas
El servicio SHALL procesar cada trabajo de forma diferida, recorriendo las etapas del contrato hasta `ready_for_review` o `failed`, y SHALL permitir consultar en cualquier momento su estado, su etapa y su intento. Un fallo transitorio SHALL dejar el trabajo en `retry_wait` y SHALL reintentarse solo, tras una espera que crece con cada intento, hasta el número máximo de intentos configurado; un fallo que no es transitorio, o el último intento fallido, SHALL dejarlo en `failed` (RNF-05, ADR-0002).

#### Scenario: Trabajo en curso
- **WHEN** una persona autorizada consulta un trabajo que se está procesando
- **THEN** recibe su estado, su etapa y su intento actuales.

#### Scenario: Trabajo terminado
- **WHEN** el procesamiento termina sin errores
- **THEN** el trabajo pasa a `ready_for_review`.

#### Scenario: Fallo transitorio
- **WHEN** una etapa falla por un error transitorio, como un modelo que no está disponible, y al trabajo le quedan intentos
- **THEN** el trabajo pasa a `retry_wait` con la etapa que falló y un error del contrato marcado como reintentable, y vuelve a procesarse cuando pasa la espera.

#### Scenario: Intentos agotados
- **WHEN** falla por un error transitorio el último intento permitido de un trabajo
- **THEN** el trabajo pasa a `failed` con un código de error del contrato que ya no es reintentable, y no queda ningún resultado consultable.

#### Scenario: Fallo que no es transitorio
- **WHEN** una etapa falla por un error que no se arregla reintentando, como un audio que no se puede decodificar
- **THEN** el trabajo pasa a `failed` sin reintentarse, con un código de error del contrato, y no queda ningún resultado consultable.

#### Scenario: Reinicio del worker
- **WHEN** el worker se reinicia con un trabajo a medias al que le quedan intentos
- **THEN** el trabajo vuelve a la cola y termina de procesarse, sin quedarse bloqueado (ADR-0002).

#### Scenario: Trabajo que tumba el worker
- **WHEN** el worker se reinicia con un trabajo a medias que ya ha agotado los intentos permitidos
- **THEN** el trabajo pasa a `failed` en lugar de volver a la cola.
