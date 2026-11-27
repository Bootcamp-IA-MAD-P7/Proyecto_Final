# Design

## Context

Véase [proposal.md](proposal.md). Los tres procesos Python reciben hoy `backend/.env` mediante Compose. `Settings` solo comprueba la longitud del secreto cuando se emiten o verifican tokens, por lo que una configuración insegura puede permitir que un proceso alcance su bucle de trabajo. `make up-prod` combina `compose.yaml` y `compose.production.yaml`; la segunda no define todavía un entorno de producción ni sustituye explícitamente el secreto heredado.

La operación debe respetar RNF-01 y los límites de secretos de ADR-0004 y ADR-0005, sin modificar la API ni el contrato.

## Goals / Non-Goals

**Goals:**

- Fallar pronto y con un mensaje seguro si falta la variable necesaria al componer el entorno de producción local.
- Aplicar una defensa en profundidad en la configuración que comparten API, worker y maintenance, incluso si el proceso se invoca fuera de Compose.
- Mantener la modalidad de desarrollo sin requisitos nuevos y documentar una demo local segura.

**Non-Goals:**

- Cambiar el formato, emisor, audiencia, caducidad o autorización de los tokens.
- Gestionar secretos con un proveedor externo, rotarlos o introducir un servicio de configuración.
- Duplicar comprobaciones en el Makefile, alterar OpenAPI o cambiar el contrato API.

## Decisions

### Compose declara explícitamente la configuración de producción de los tres procesos

`compose.production.yaml` declarará `APP_ENV=production` y mapeará el `AUTH_SECRET` del entorno de Compose en backend, worker y maintenance mediante una interpolación que rechace valores ausentes o vacíos. Un valor definido en `environment` tiene prioridad sobre `env_file`; por tanto, el valor documentado para desarrollo que pudiera figurar en `backend/.env` no podrá eludir el requisito.

Se elige la validación de interpolación de Compose para fallar antes de crear contenedores. Se descarta comprobar la variable en el Makefile: duplicaría reglas de seguridad y no cubriría invocaciones directas de Compose.

### Settings valida por modo de ejecución, antes de iniciar trabajo

`Settings` incorporará el modo de aplicación, con desarrollo como valor por defecto para compatibilidad. En producción centralizará la validación de presencia, longitud mínima vigente y no reutilización del centinela documentado para desarrollo. Backend, worker y maintenance ya construyen `Settings` al arrancar, por lo que la misma validación protege los tres puntos de entrada y ejecuciones que no usen Compose.

La validación usará mensajes estables que indiquen la condición incumplida sin interpolar el secreto, token ni configuración completa. Se descarta basarla solo en la emisión de tokens porque worker y maintenance deben rechazar una configuración insegura antes de procesar datos.

### Ejemplos y guía sin valores secretos

El ejemplo de entorno raíz y el README indicarán dónde definir una clave propia para `make up-prod`, cómo generarla localmente y que no debe versionarse. No se añadirá un secreto real ni se copiará el centinela de desarrollo al entorno raíz. La guía cubrirá solo la demo local, acorde con ADR-0005.

## Risks / Trade-offs

- [Un usuario ejecuta Compose sin exportar la variable] → La interpolación falla antes de crear procesos y el README explica la configuración requerida.
- [Un proceso se inicia directamente o se configura manualmente] → La comprobación en `Settings` repite la defensa sin depender de Compose.
- [La validación accidentalmente afecta al desarrollo] → El modo por defecto seguirá siendo desarrollo y las pruebas cubrirán los arranques existentes.
- [Un mensaje o una aserción filtra el secreto] → Las pruebas comprobarán que errores y logs contienen solo el nombre o la regla de la variable, nunca su valor.

## Migration Plan

1. Añadir la validación y sus pruebas sin cambiar la interfaz HTTP.
2. Configurar el entorno de producción de los tres servicios y actualizar ejemplos y README.
3. Verificar configuración Compose, pruebas de backend y los checks habituales antes de usar `make up-prod` con una clave local propia.
4. Para revertir, restaurar la configuración y el código anteriores; no hay migraciones de datos ni secretos versionados que recuperar.
