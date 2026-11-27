# Tasks

## 1. Exigir un secreto propio en producción local (configuración y backend) · #63

**Criterios de aceptación:**

- `make up-prod` rechaza antes de crear backend, worker o maintenance un `AUTH_SECRET` ausente o vacío, con un mensaje claro que no revela su valor.
- Backend, worker y maintenance reciben explícitamente `APP_ENV=production` y el mismo secreto exigido desde el entorno de Compose; un valor de `backend/.env` no puede sustituirlo.
- En modo producción, los tres entry points rechazan secretos ausentes, vacíos, demasiado cortos o iguales al centinela documentado de desarrollo antes de atender trabajo; los errores y logs no contienen secretos ni tokens.
- Un secreto propio de longitud válida permite el arranque de los tres procesos y el flujo de desarrollo mediante `make up` conserva su comportamiento actual.
- README y el ejemplo de entorno explican configurar una demo local de producción sin versionar secretos reales.

**Depende de:** —

- [x] 1.1 Centralizar en `Settings` la validación del modo de producción y añadir pruebas unitarias para secreto ausente, vacío, demasiado corto, centinela de desarrollo y secreto propio válido; verificar que los mensajes no contienen el valor aportado.
- [x] 1.2 Aplicar `APP_ENV=production` y el requisito de `AUTH_SECRET` en `compose.production.yaml` para backend, worker y maintenance, con prioridad sobre `backend/.env`; verificar con la configuración de Compose los casos ausente, vacío y válido sin imprimir el secreto.
- [x] 1.3 Probar que los entry points de API, worker y maintenance rechazan la configuración de producción inválida antes de iniciar trabajo y conservan los arranques de desarrollo existentes; ejecutar las pruebas de backend afectadas.
- [x] 1.4 Actualizar `.env.example`, README y, si procede, la documentación operativa para una demo local segura; verificar que no incorporan secretos y que las instrucciones de `make up-prod` reflejan el requisito.
- [x] 1.5 Ejecutar los objetivos de lint y test afectados, `openspec validate fix-production-auth-secret --strict` y `git diff --check`; verificar que no cambia OpenAPI ni el contrato API.

## Workflow follow-up

- Tras la revisión humana y la validación de la implementación de la #63, sincronizar y archivar este cambio conforme a WORKFLOW §6.
