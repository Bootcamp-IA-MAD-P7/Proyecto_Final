# Design

## Context

Ver proposal.md para motivación y límites. No hay specs previas; PRD en borrador, arquitectura Candidata y ADR-0001 a 0004 Propuestos. Este cambio propone comportamiento de interfaz, no acepta stack ni implementa servicios. Épica y ROADMAP pendientes.

## Goals / Non-Goals

**Goals:** contrato independiente de modelos y framework, ejemplos utilizables por las tres capas y criterios comunes de aceptación.
**Non-Goals:** implementar API, cola, IA, interfaz o planificar aquí todo el MVP. RF-06/RF-07 excluidos; marcas temporales de transcripción permanecen.

## Decisions

Todas las elecciones siguientes son propuestas técnicas para revisión.

### Fuente única y representación

Contrato inicial 0.1.0, endpoints /v1, JSON UTF-8 y fechas UTC ISO 8601. IDs opacos no vacíos; no imponer UUID a consumidores. Versiones de resultado enteras positivas independientes de schema_version. No introducir tablas SQL ni estructuras del modelo en la interfaz pública.

En este borrador el diseño es dueño de campos, la spec de invariantes y examples.md de ejemplos ilustrativos. Al ejecutar la historia 1, OpenAPI y JSON Schema serán normativos junto al productor, enlazados desde docs/CONTRACTS; retirar de este diseño las tablas duplicadas a favor de enlaces al estabilizarlo. Alternativa descartada: copiar modelos distintos en cada capa, por divergencia y dependencia de integración.

### Endpoints y errores

| Operación | Entrada | Salida / errores específicos |
|---|---|---|
| POST /v1/classes | multipart: audio binario y metadata JSON; Idempotency-Key | 202: class_id, job_id, state; 409 clave distinta, 413 tamaño, 415 formato, 422 metadatos |
| GET /v1/jobs/{job_id} | identidad del solicitante | 200: job_id, class_id, state, stage, attempt, error nullable |
| GET /v1/classes/{class_id}/result | identidad del solicitante | 200 resultado visible; 409 result_not_ready si aún no existe para docente; 404 para recurso invisible al alumno |
| PATCH /v1/classes/{class_id}/review | expected_result_version, changes | 200 nueva versión; 409 obsoleta; 422 referencia inválida |
| POST /v1/classes/{class_id}/approve | expected_result_version | 200 publicación de esa versión; 409 obsoleta |

Común: 401 credencial inválida; 403 operación prohibida en clase visible; 404 inexistente o clase ajena para no revelar existencia; 503 indisponibilidad transitoria. Error común: error.code, error.message seguro, error.retryable, request_id. Nunca incluir stack traces, tokens o audio. Reintentar una carga tras fallo de conexión conserva Idempotency-Key. Retención de esas claves pendiente de dimensionamiento.

### Datos compartidos

| Objeto | Campos propuestos e invariantes |
|---|---|
| Metadata | external_class_id, participant_count positivo, participants con participant_id único, role teacher/student, display_name opcional; consent_reference. Número y lista coherentes; no asignan permisos por sí mismos |
| Job | job_id, class_id, state, stage nullable, attempt entero no negativo, error nullable; sin rutas locales ni lease_token público |
| Transcript | speakers: speaker_id de sesión y participant_id nullable; segments: segment_id, start_ms/end_ms enteros no negativos con fin mayor que inicio, speaker_id existente, text |
| Analysis | general_summary texto; items con item_id, category, content; categorías vocabulary, grammar, errors_corrections, reinforced_successes, key_concepts, resolved_questions |
| Result | schema_version, class_id, result_version, transcript, analysis, review, publication |
| Review | status pending/in_review/approved, review_due_at; no fija 24 horas en esquema |
| Publication | status unpublished/published, result_version nullable, published_at nullable, mode nullable teacher_approved/automatic |
| Changes | transcript/analysis corregidos y asociaciones speaker_id → participant_id; no se puede editar identidad de clase, permisos, publicación ni plazo |
| StageResult interno | job_id, lease_token, stage, model_revision, payload, warnings; separado de API pública |

consent_reference es obligatorio: su ausencia o invalidez según el contrato devuelve 422 invalid_consent_reference, sin aceptar trabajo ni iniciar inferencia. Recibir la referencia y validar su estructura no demuestra que exista consentimiento. El mecanismo y la responsabilidad de verificar el consentimiento referenciado siguen pendientes de acordar; no se consideran resueltos por esta validación de metadatos.

Estados de trabajo candidatos: queued, normalizing, transcribing, diarizing, analyzing, retry_wait, ready_for_review, published, failed, expired. Secuencia normal conforme a arquitectura. retry_wait conserva etapa para reanudar; failed/expired no son resultados completos. La expiración del audio es independiente de publicación: no elimina automáticamente una transcripción publicada.

No restringir igualdad de número detectado de hablantes y participantes: silencio y solapamientos pueden producir discrepancias; la asociación manual admite null. Correcciones no trasladan participantes entre clases. Para RF-07 no se añaden campos temporales a los ítems pedagógicos.

### Revisión y publicación provisional

El contrato permite plazo variable. Ejemplo de 24 horas solo para ilustrar RD-06 provisional; no supone validación por Lay. Contar desde ready_for_review y mantener un vencimiento por revisión son opciones del ADR-0004 pendientes. No se especifica una salida normativa para in_review sin aprobación al vencer ni edición posterior a publicación: resolver antes de implementar RF-05. No convertir la sugerencia de bloqueo de arquitectura en un requisito aprobado. Publicación equivale a consulta autorizada, sin añadir correo.

### Propiedad de specs posteriores

| Spec a preparar | Dueña de | Depende de |
|---|---|---|
| audio-job-intake | RF-01: validación real de audio, aceptación durable, recuperación y expiración | mvp-service-contracts, walking skeleton |
| session-transcription | RF-02: transcripción, diarización, calidad y asignación de hablantes | contrato; integración con intake |
| pedagogical-analysis | RF-03: extracción, resumen, evidencia y calidad | contrato; transcripción para integración |
| structured-results | RF-04: disponibilidad y consulta de versión visible | contrato; productores de resultados |
| teacher-review-publication | RF-05: edición, aprobación, temporizador y concurrencia | contrato; structured-results; decisiones Lay |

Estas specs referenciarán invariantes comunes de mvp-service-contracts y el contrato normativo, sin copiar campos ni reglas de acceso. RNF-02 se desarrollará en gestión del audio; no duplicar su regla de retención en análisis. Cada funcionalidad posterior tendrá su propio cambio y tasks por historias, no cinco cambios creados sin revisar sus dependencias.

### Paralelismo recomendado

Cerrar contrato primero y planificar walking skeleton como primera épica operativa, con servicios y ambos entornos desplegados. Después persona A aborda recepción/persistencia y consulta; B transcripción y análisis, secuenciales en integración pero probables con fixtures independientes; C interfaz y revisión contra ejemplos sintéticos. A comparte con C publicación/temporizador. Integración final depende de todas las capas y datos autorizados. El backend no debe esperar al modelo real para probar errores, permisos o revisión.

## Risks / Trade-offs

- Contrato preliminar con producto abierto → revisar decisiones pendientes antes de ejecutar historias; validación estructural no equivale a aprobación.
- Requisitos de IA mezclados con interfaz → evaluar calidad en specs funcionales, no por JSON válido.
- Identidad de voz confundida con usuario → mantener speaker_id separado y asociación explícita.
- Muchos campos compartidos → un único artefacto normativo y ejemplos validados contra él durante apply.
- Contratos listos sin infraestructura → no omitir walking skeleton ni declarar MVP implementado.

## Migration Plan

No hay clientes publicados ni migración de datos. Tras aprobación, registrar contrato Propuesto 0.1.0, validar ejemplos, desarrollar consumidores con mocks y comprobar compatibilidad antes de activar endpoints. Si cambia el borrador, actualizar conjuntamente fixtures; no archivar specs como implementadas antes de completar las tareas de contrato.

## Open Questions

Bloqueos de aprobación, conservados por petición del usuario: idiomas/calidad, formatos/límites, contrato de identidad y consentimiento; plazo de Lay, origen del temporizador, revisión incompleta y edición posterior. No se inventan respuestas: los casos decididos sí tienen escenarios y los restantes bloquean su implementación específica. Épica y aprobación de fase 1 deben resolverse antes de publicar el plan. ADR siguen Propuestos.
