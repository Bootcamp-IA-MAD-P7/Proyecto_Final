# Design

## Context

`make ci` ejecuta lint y pruebas en imágenes de desarrollo y termina con un build de `compose.production.yaml`. Compose necesita interpolar `AUTH_SECRET` para ese build, aunque no se inicien los servicios de producción.

## Goals / Non-Goals

**Goals:**

- Permitir que `make ci` se ejecute sin configuración previa de secretos.
- Limitar una clave sintética y aleatoria al proceso de CI.
- Conservar el rechazo de `make up-prod` sin un secreto propio.

**Non-Goals:**

- Añadir secretos versionados, valores por defecto de producción o cambios en Compose.
- Cambiar autenticación, OpenAPI, contrato API o el entorno de desarrollo.

## Decisions

### La receta genera la clave en el proceso de CI

La receta `ci` generará una clave de longitud suficiente en la shell que invoca el build de producción y la exportará solo para ese comando. No se escribirá en `.env`, no se imprimirá y no existirá fuera de la ejecución.

Se descarta un valor fijo en el Makefile o `compose.production.yaml`, porque rebajaría la protección de `make up-prod`.

### La regresión se prueba a nivel de receta

Una prueba de integración de configuración verificará que la receta o su equivalente controlado construye producción sin `AUTH_SECRET` previo y que `make up-prod` sigue rechazando valores ausentes.

## Risks / Trade-offs

- [La generación no está disponible en una shell compatible] → usar utilidades ya presentes en la imagen o shell del proyecto y documentar el requisito mínimo.
- [La clave se filtra a la salida] → no expandirla ni imprimir el entorno; la prueba inspecciona la salida.
