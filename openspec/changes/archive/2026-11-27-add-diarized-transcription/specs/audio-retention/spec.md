# Spec Delta

## MODIFIED Requirements

### Requirement: Trabajos caducados
Cuando vence el plazo de un audio cuyo trabajo no ha terminado, también si está en espera de reintento, el servicio SHALL dejar el trabajo en `expired` y no SHALL procesarlo más. Los resultados ya terminados se conservan: solo se purga el audio (RNF-02).

#### Scenario: Trabajo sin terminar
- **WHEN** vence el plazo de un audio cuyo trabajo está en cola, en curso o en espera de reintento
- **THEN** el trabajo pasa a `expired`, se consulta con ese estado y no se reclama de nuevo.

#### Scenario: Resultado ya listo
- **WHEN** vence el plazo de un audio cuyo trabajo está en `ready_for_review`
- **THEN** el audio se purga y el trabajo y su resultado siguen disponibles como antes.
