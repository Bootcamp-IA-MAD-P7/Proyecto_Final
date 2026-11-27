# Spec Delta

## Purpose

Que el audio original de una clase se conserve en infraestructura propia solo durante el plazo de 14 días y después deje de estar disponible para consulta o procesamiento ([ADR-0004](../../../../../docs/ADR/0004-access-and-retention.md)).

## ADDED Requirements

### Requirement: Plazo de conservación registrado
Al guardar el audio de una clase, el servicio SHALL registrar su momento de recepción y su fecha de purga, 14 días después de la recepción (RNF-02).

#### Scenario: Audio recibido
- **WHEN** se acepta el envío de una clase
- **THEN** su audio queda registrado con el momento de recepción y una fecha de purga 14 días posterior.

### Requirement: Purga del audio vencido
El servicio SHALL eliminar el audio original y sus copias de trabajo cuando vence su plazo, sin necesitar que el worker esté libre, y SHALL reintentar el borrado si falla. También SHALL purgar los audios vencidos al arrancar, antes de retomar trabajos (RNF-02).

#### Scenario: Plazo vencido
- **WHEN** vence la fecha de purga de un audio
- **THEN** en el siguiente ciclo de mantenimiento el audio y sus copias se eliminan y queda registrado cuándo se borró.

#### Scenario: Borrado fallido
- **WHEN** el borrado físico de un audio vencido falla
- **THEN** el audio sigue sin estar disponible, el fallo queda en el log sin datos de la clase y se reintenta en el siguiente ciclo.

#### Scenario: Procesamiento en curso
- **WHEN** vence el plazo de un audio mientras el worker procesa su trabajo
- **THEN** el audio se purga igualmente y el resultado que llegue después se descarta.

### Requirement: Trabajos caducados
Cuando vence el plazo de un audio cuyo trabajo no ha terminado, el servicio SHALL dejar el trabajo en `expired` y no SHALL procesarlo más. Los resultados ya terminados se conservan: solo se purga el audio (RNF-02).

#### Scenario: Trabajo sin terminar
- **WHEN** vence el plazo de un audio cuyo trabajo está en cola o en curso
- **THEN** el trabajo pasa a `expired`, se consulta con ese estado y no se reclama de nuevo.

#### Scenario: Resultado ya listo
- **WHEN** vence el plazo de un audio cuyo trabajo está en `ready_for_review`
- **THEN** el audio se purga y el trabajo y su resultado siguen disponibles como antes.

### Requirement: Sin archivos huérfanos
El servicio SHALL eliminar los archivos de audio que una carga fallida haya dejado sin clase asociada (RNF-02).

#### Scenario: Carga interrumpida
- **WHEN** una carga se interrumpe después de escribir el archivo y antes de crear la clase
- **THEN** el archivo se elimina en un ciclo de mantenimiento posterior y nunca se procesa.
