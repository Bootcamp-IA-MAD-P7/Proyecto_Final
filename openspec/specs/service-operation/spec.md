# service-operation Specification

## Purpose
Que se pueda saber si el servicio está vivo y si sus procesos trabajan, sin exponer datos de clases.

## Requirements

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

### Requirement: Secreto de autenticación obligatorio en producción local
La configuración de producción local SHALL exigir un `AUTH_SECRET` no vacío y propio antes de iniciar backend, worker o maintenance. Los tres procesos SHALL recibir la misma configuración de autenticación de producción, que prevalecerá sobre valores de desarrollo cargados desde archivos de entorno del backend (RNF-01, ADR-0004, ADR-0005).

#### Scenario: Secreto ausente al iniciar producción
- **WHEN** se ejecuta `make up-prod` sin definir `AUTH_SECRET`
- **THEN** la configuración rechaza el arranque antes de crear los procesos afectados e informa de la variable necesaria sin mostrar ningún secreto.

#### Scenario: Secreto vacío al iniciar producción
- **WHEN** se ejecuta `make up-prod` con `AUTH_SECRET` vacío
- **THEN** la configuración rechaza el arranque antes de crear los procesos afectados e informa del requisito sin mostrar ningún secreto.

### Requirement: Secreto válido y no reutilizado en producción
En modo producción, cada proceso SHALL rechazar un secreto ausente, vacío, demasiado corto o igual al secreto de desarrollo documentado. Los errores y logs de configuración SHALL identificar el requisito incumplido sin incluir el valor del secreto ni tokens derivados (RNF-01, ADR-0004).

#### Scenario: Secreto demasiado corto
- **WHEN** backend, worker o maintenance se inicia en modo producción con un `AUTH_SECRET` demasiado corto
- **THEN** el proceso rechaza su configuración antes de atender trabajo y comunica un error seguro.

#### Scenario: Secreto de desarrollo en producción
- **WHEN** backend, worker o maintenance se inicia en modo producción con el secreto documentado para desarrollo
- **THEN** el proceso rechaza su configuración antes de atender trabajo y no registra el valor recibido.

#### Scenario: Secreto propio válido en producción
- **WHEN** backend, worker y maintenance se inician en modo producción con un secreto propio de longitud válida
- **THEN** aceptan la configuración sin exponer el secreto en su salida de arranque.

### Requirement: Desarrollo sin requisito adicional de secreto de producción
La protección de producción SHALL aplicarse solo cuando se declara el modo de producción. El arranque de desarrollo SHALL conservar su configuración y comportamiento actuales, sin requerir una variable adicional en el entorno raíz (RNF-01).

#### Scenario: Arranque de desarrollo
- **WHEN** se ejecuta `make up` con la configuración de desarrollo existente
- **THEN** los servicios conservan su comportamiento actual y no se les exige un secreto de producción en el entorno raíz.
