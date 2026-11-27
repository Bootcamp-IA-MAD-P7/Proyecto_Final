# Tasks

## 1. Restaurar el build de producción en CI (configuración) · #63

**Criterios de aceptación:**

- `make ci` construye las imágenes de producción sin que quien lo ejecuta defina `AUTH_SECRET`.
- La clave usada para la interpolación de CI es aleatoria, no se versiona, no se escribe en `.env` ni se muestra en la salida.
- `make up-prod` conserva el rechazo de `AUTH_SECRET` ausente o vacío y no adquiere valores por defecto.
- Las pruebas cubren la regresión y no cambian OpenAPI ni el contrato API.

**Depende de:** —

- [x] 1.1 Ajustar la receta `ci` para generar y limitar una clave temporal al build de producción; verificar que no cambia `make up-prod`.
- [x] 1.2 Añadir una prueba de regresión de la configuración de CI y actualizar la documentación operativa si procede; verificar que no incorpora secretos.
- [x] 1.3 Ejecutar `make ci` sin `AUTH_SECRET` predefinido, los checks afectados, OpenSpec estricto y `git diff --check`.
