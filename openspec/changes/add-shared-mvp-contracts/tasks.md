# Tasks

Plan de la funcionalidad de contratos, no del MVP completo. Ninguna tarea ejecutada. Antes de apply: aprobar este plan, cerrar decisiones que afecten al contrato, completar la fase 1 y vincular la épica/Issues. Las historias de implementación funcional se preparan después según design.md.

## 1. Registrar el contrato compartido del MVP (contrato)

**Criterios de aceptación:**
- OpenAPI/JSON Schema propuestos 0.1.0 cubren endpoints, representaciones y errores del diseño.
- Los escenarios de la spec tienen correspondencia con validaciones del contrato o pruebas futuras de comportamiento.
- No se fija el plazo provisional como constante ni se da por aprobado un ADR.

**Depende de:** —

- [ ] 1.1 Registrar campos, restricciones, endpoints y compatibilidad en un artefacto normativo junto al productor; comprobar su validación con herramientas acordadas en el plan aprobado.
- [ ] 1.2 Registrar contrato y versión en docs/CONTRACTS y su índice, enlazando los artefactos sin duplicarlos; comprobar referencias.
- [ ] 1.3 Resolver y documentar límites/formatos, identidad y políticas pendientes antes de fijar sus pruebas; contrastar con aprobación explícita y PRD.

## 2. Preparar casos de conformidad de API (backend)

**Criterios de aceptación:**
- Casos positivos y negativos cubren recepción, consulta, permisos y conflictos sin depender de modelos.
- Cada caso indica entrada, resultado esperado y requisito de origen.

**Depende de:** 1

- [ ] 2.1 Preparar fixtures de carga, idempotencia y errores HTTP; comprobar que ejemplos válidos cumplen esquema y negativos fallan donde corresponde.
- [ ] 2.2 Definir pruebas de contrato para acceso cruzado, borradores y versiones obsoletas; revisar matriz docente/alumno/emisor con la spec y documentar cómo ejecutarlas cuando exista API.

## 3. Preparar casos de conformidad de inferencia (procesamiento)

**Criterios de aceptación:**
- Transcripción, hablantes y análisis tienen fixtures sin datos reales.
- Los casos no exigen una biblioteca ni calidad de modelo aún no validada.

**Depende de:** 1

- [ ] 3.1 Preparar resultados de etapa y completos, incluidos hablante sin asignar y categorías vacías; validarlos contra el esquema compartido.
- [ ] 3.2 Preparar casos inválidos de intervalos, referencias y categorías; comprobar rechazo y documentar la frontera entre formato y calidad pedagógica.

## 4. Preparar casos de consumo y revisión (interfaz)

**Criterios de aceptación:**
- El consumidor dispone de ejemplos de espera, fallo, borrador, edición y publicación.
- RF-06/RF-07 no se incorporan a los ejemplos del MVP.

**Depende de:** 1

- [ ] 4.1 Preparar fixtures de vistas docente/alumno y secuencias de corrección/aprobación; validarlos contra contrato y documentar diferencias de visibilidad.
- [ ] 4.2 Preparar secuencia temporal parametrizada sin revisión y caso de conflicto concurrente; verificar expectativas frente a RF-05, marcando validación Lay pendiente donde corresponda.

## 5. Verificar el contrato entre consumidores (integración)

**Criterios de aceptación:**
- Los tres conjuntos de fixtures usan las mismas identidades, estados, errores y versión.
- No quedan divergencias de interfaz ni se afirma que el runtime esté implementado.

**Depende de:** 1, 2, 3, 4

- [ ] 5.1 Ejecutar validación conjunta de fixtures y referencias; entregar informe de conformidad con los escenarios de mvp-service-contracts.
- [ ] 5.2 Ejecutar verify del cambio completo y openspec validate; corregir discrepancias y pasar reviewer antes de publicación autorizada.

## Workflow follow-up

- Crear Issues y publicar el plan solo después de aprobación y autorización para operaciones Git/GitHub.
- El cambio de contratos entrega un contrato verificable; los endpoints y modelos se implementan en los cambios funcionales siguientes.
- La integración completa de este cambio hace sync/archive una vez según WORKFLOW, tras revisar la conformidad del contrato; no atribuye implementación de RF-01 a RF-05.
