# Proposal

## Why

La Issue #63 hizo obligatorio `AUTH_SECRET` en Compose de producción. `make ci` también resuelve esa composición para construir imágenes y ahora falla sin que quien desarrolla configure un secreto de producción, aunque no arranque producción.

## What Changes

- Aportar una clave generada exclusivamente durante `make ci` para la interpolación del build de producción.
- Mantener el requisito de un secreto propio, ausente de valores por defecto, para `make up-prod`.
- Añadir una prueba de regresión de la receta y documentar el alcance efímero de la clave de CI.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- Ninguna: no cambia comportamiento de producto ni operación de producción.

## Impact

- Makefile, pruebas de la configuración de CI y README si necesita aclarar la diferencia entre CI y `make up-prod`.
- Sin cambios de OpenAPI, contrato API, servicios de producción ni archivos `.env`.
