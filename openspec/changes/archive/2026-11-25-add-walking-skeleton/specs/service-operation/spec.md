# Spec Delta

## Purpose

Que se pueda saber si el servicio está vivo y si sus procesos trabajan, sin exponer datos de clases.

## ADDED Requirements

### Requirement: Salud y disponibilidad de la API
La API SHALL exponer un punto de salud que responde mientras el proceso está vivo y un punto de disponibilidad que indica si sus dependencias, como la base de datos, están accesibles, sin incluir credenciales, cadenas de conexión ni datos de clases (RNF-01).

#### Scenario: API viva
- **WHEN** se consulta `GET /health` con la API arrancada
- **THEN** responde 200, aunque la base de datos no esté disponible.

#### Scenario: Dependencia caída
- **WHEN** se consulta `GET /ready` y la base de datos no responde
- **THEN** responde 503 e indica qué dependencia no está disponible, sin credenciales ni cadenas de conexión.

#### Scenario: Todo disponible
- **WHEN** se consulta `GET /ready` con la base de datos accesible
- **THEN** responde 200.

### Requirement: Actividad observable de los procesos de fondo
El worker y el proceso de mantenimiento SHALL registrar su arranque y su actividad en logs estructurados que no incluyan audio, transcripciones, nombres ni tokens (RNF-01).

#### Scenario: Arranque del worker
- **WHEN** el worker arranca
- **THEN** registra que está listo y cuántos trabajos en curso ha devuelto a la cola.

#### Scenario: Ciclo de mantenimiento
- **WHEN** se cumple el intervalo configurado de mantenimiento
- **THEN** el proceso registra que ha ejecutado su ciclo.
