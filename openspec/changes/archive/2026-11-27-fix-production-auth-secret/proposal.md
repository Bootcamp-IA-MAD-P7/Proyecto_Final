# Proposal

## Why

La Issue [#63](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/63) corrige una configuración insegura de la modalidad de producción local: `make up-prod` puede iniciar los procesos con el secreto documentado para desarrollo. La configuración de producción debe requerir una clave propia antes de poner en marcha backend, worker y maintenance.

## What Changes

- Exigir desde Docker Compose una variable `AUTH_SECRET` no vacía para `make up-prod`, aplicada de forma idéntica a backend, worker y maintenance y con prioridad sobre `backend/.env`.
- Declarar `APP_ENV=production` para esos tres procesos y hacer que su configuración rechace secretos ausentes, vacíos, demasiado cortos o iguales al secreto de desarrollo documentado, sin mostrar el valor en errores ni logs.
- Conservar el comportamiento de desarrollo de `make up` y de `backend/.env`.
- Documentar cómo configurar una clave local propia para una demo con `make up-prod`, sin versionar secretos.
- Añadir pruebas positivas y negativas de la configuración y de los entry points afectados.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `service-operation`: arranque seguro de los procesos de producción local con una configuración de autenticación válida (RNF-01, ADR-0004, ADR-0005).

## Impact

- Configuración: `compose.production.yaml` y `.env.example`; no se cambia el Makefile ni se duplica su validación.
- Backend: `Settings` y los entry points de API, worker y maintenance, con pruebas unitarias y de proceso.
- Documentación: README y, si refleja el modo de arranque, ARCHITECTURE.
- No cambia OpenAPI, el contrato API, el esquema de datos, el flujo de desarrollo ni las funciones de autenticación expuestas.
