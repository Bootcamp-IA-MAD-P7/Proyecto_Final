# Catálogo de historias del MVP

Estado: propuesta para revisión, 23 de noviembre de 2026. Demo: 11 de diciembre; entrega: 15 de diciembre de 2026. No constituye aprobación del PRD (Borrador), arquitectura (Candidata) ni ADR (Propuestos). RF-06 y RF-07 excluidos; sí se conservan tiempos de transcripción.

## Convenciones y preparación para Issues

No existía documento equivalente en docs/. Este catálogo es material de revisión, no fuente de avance. WORKFLOW exige aprobar fase 1 y ROADMAP, luego specs y tasks por funcionalidad antes de crear Issues. Al trasladar estas fichas, criterios y tareas vivirán en tasks.md y la Issue enlazará su sección conforme a la plantilla, evitando dos fuentes normativas. Ninguna historia está Ready.

La consulta gh label list falló por conexión a api.github.com; gh project list devolvió unknown owner type. No se verificó configuración remota ni se presume ausencia de Project. Se reutilizan labels locales de ISSUE_LABELS: story, feature/test/chore/docs y priority: high/medium. No crear equivalentes type:feature ni priority:high. Nuevas propuestas pendientes: area:backend, area:inference, area:frontend, area:devops y scope:mvp. No usar blocked/ready como estados duplicados: dependencias nativas y, si se confirma Project, Backlog → Ready → In Progress → In Review → Done. Decisiones pendientes en campo/texto, sin nueva label de estado.

## Épicas y fuentes

E1 Contratos compartidos y walking skeleton; E2 Recepción de audio y gestión de trabajos; E3 Transcripción y diarización; E4 Análisis pedagógico y resumen general; E5 Resultados estructurados; E6 Revisión docente y publicación; E7 Interfaz web React; E8 Privacidad, pruebas e integración del MVP.

Referencias comunes: [PRD](PRD.md), [arquitectura](ARCHITECTURE.md), [ADR](ADR/README.md), [workflow](../WORKFLOW.md), [contrato OpenSpec](../openspec/changes/add-shared-mvp-contracts/specs/mvp-service-contracts/spec.md), [diseño](../openspec/changes/add-shared-mvp-contracts/design.md) y [ejemplos](../openspec/changes/add-shared-mvp-contracts/examples.md).

US-001–005 corresponden exactamente a tasks §1–5 del cambio existente; no son implementación de endpoints. El resto requiere cambios nuevos: skeleton (006–007), audio-job-intake (008–010), session-transcription (011–012), pedagogical-analysis (013–014), structured-results (015–016), teacher-review-publication (017–019), demo-interface (020–022), privacy-and-mvp-integration (023–024). Son agrupaciones propuestas: cada cambio referenciará contrato común sin duplicarlo y tendrá integración final dependiente de todas sus secciones. Los cambios funcionales aún no existen.

## Resumen

Personas A, B y C son perfiles provisionales, sin asignaciones. Prioridad alta para camino crítico; media para fixtures paralelizables, que siguen siendo obligatorios.

| ID | Historia | Épica | Prioridad | Labels (nuevas: area:* y scope:mvp) | Dependencias de cierre (detalle en ficha) | Persona | Hito objetivo |
|---|---|---|---|---|---|---|---|
| US-001 | Contrato versionado | E1 | high | story, docs, priority: high, area:backend, scope:mvp | — | A | Demo 11/12 |
| US-002 | Conformidad API | E1 | medium | story, test, priority: medium, area:backend, scope:mvp | 001 | C | Demo 11/12 |
| US-003 | Conformidad de inferencia | E1 | medium | story, test, priority: medium, area:inference, scope:mvp | 001 | B | Demo 11/12 |
| US-004 | Conformidad de interfaz | E1 | medium | story, test, priority: medium, area:frontend, scope:mvp | 001 | C | Demo 11/12 |
| US-005 | Integración del contrato | E1 | medium | story, test, priority: medium, area:frontend, scope:mvp | 001,002,003,004 | C | Demo 11/12 |
| US-006 | Skeleton desplegado | E1 | high | story, chore, priority: high, area:devops, scope:mvp | 001 | A | Demo 11/12 |
| US-007 | CI e integración del skeleton | E1 | high | story, chore, priority: high, area:devops, scope:mvp | 006 | C | Demo 11/12 |
| US-008 | Carga durable e idempotente | E2 | high | story, feature, priority: high, area:backend, scope:mvp | 005,007; verificación de seguridad en 016 y consentimiento real en 023 para uso real | A | Demo 11/12 |
| US-009 | Ejecución y recuperación de trabajos | E2 | high | story, feature, priority: high, area:backend, scope:mvp | 008,007 | A | Demo 11/12 |
| US-010 | Integración de recepción | E2 | high | story, test, priority: high, area:frontend, scope:mvp | 005,007,008,009 | C | Demo 11/12 |
| US-011 | Transcripción normalizada | E3 | high | story, feature, priority: high, area:inference, scope:mvp | 003,007; idiomas y umbrales para aceptación de calidad | B | Demo 11/12 |
| US-012 | Diarización e integración de hablantes | E3 | high | story, feature, priority: high, area:inference, scope:mvp | 009,011; corpus y umbrales acordados | B | Demo 11/12 |
| US-013 | Repaso y resumen general | E4 | high | story, feature, priority: high, area:inference, scope:mvp | 003,007; modelo y parámetros evaluados | B | Demo 11/12 |
| US-014 | Evaluación e integración pedagógica | E4 | high | story, test, priority: high, area:inference, scope:mvp | 009,012,013; idiomas y umbrales Lay | B | Demo 11/12 |
| US-015 | Persistencia y consulta de versiones | E5 | high | story, feature, priority: high, area:backend, scope:mvp | 005,007; matriz de seguridad 016 para integración pública | A | Demo 11/12 |
| US-016 | Integración de acceso por clase | E5 | high | story, test, priority: high, area:backend, scope:mvp | 008,015; revisión de endpoints posteriores en 019/022 | A | Demo 11/12 |
| US-017 | Corrección docente versionada | E6 | high | story, feature, priority: high, area:backend, scope:mvp | 015,016; política de edición posterior pendiente Lay | C | Demo 11/12 |
| US-018 | Aprobación y publicación programada | E6 | high | story, feature, priority: high, area:backend, scope:mvp | 017,016; Lay: inicio, plazo, in_review y edición posterior | A | Demo 11/12 |
| US-019 | Integración de revisión y reloj | E6 | high | story, test, priority: high, area:frontend, scope:mvp | 015,016,017,018; decisión Lay sobre caso no cubierto | C | Demo 11/12 |
| US-020 | Carga y seguimiento en la interfaz web React | E7 | high | story, feature, priority: high, area:frontend, scope:mvp | 007; 010 requerido para conexión real de 022 | C | Demo 11/12 |
| US-021 | Revisión docente y consulta en la interfaz web React | E7 | high | story, feature, priority: high, area:frontend, scope:mvp | 017,018 para conexión real; 022 verifica permisos extremo a extremo | C | Demo 11/12 |
| US-022 | Integración E2E de React con FastAPI | E7 | high | story, test, priority: high, area:frontend, scope:mvp | 010,014,016,019,020,021,023 | C | Demo 11/12 |
| US-023 | Consentimiento, purga y aislamiento | E8 | high | story, feature, priority: high, area:backend, scope:mvp | 008,009,016; ADR-0004, evidencia de consentimiento y política de copias | A | Demo 11/12 |
| US-024 | Ensayo E2E y capacidad de entrega | E8 | high | story, test, priority: high, area:inference, scope:mvp | 014,022,023 y todas las historias previas cerradas | C | Entrega 15/12 |

## DoD común (aplicable íntegramente a cada ficha)

Criterios demostrados con evidencia reproducible; tests pertinentes y make ci verdes; documentación y contratos actualizados; sin secretos ni datos reales en fixtures; verify de sección y validación OpenSpec sin discrepancias; reviewer sin hallazgos de alcance; tareas marcadas solo tras ejecución y PR revisado y mergeado por persona. Integración añade verify completo, sync y archive una sola vez según WORKFLOW. Nada de esto se ejecuta en este encargo.

## Historias detalladas


Los hitos indican cierre objetivo, no garantía. US-001–023 deben cerrar para la demo; US-024 cierra el 15/12 pero exige ensayo real previo al 11/12. Las estimaciones son jornadas-persona efectivas, incluidas pruebas propias, excluidas esperas y revisión externa. Son rangos de planificación sin medición previa. Las fichas mayores de dos jornadas requieren revisar tamaño antes de publicar y organizar incrementos internos comprobables; si no caben en un PR razonable, acordar división, sin añadir historias en este encargo.

Todas requieren plan aprobado y DoR. Las dependencias de inicio son técnicas, no sustituyen esa aprobación. Preparar fixtures no equivale a completar integración. Los criterios adicionales son propuestas para las futuras specs funcionales.

### US-001 — Contrato versionado

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: fijar un lenguaje común para que API, inferencia y cliente se implementen sin acuerdos implícitos.

**Contexto y objetivo:** cubre RF-01 a RF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** Inventariar operaciones de carga, trabajos, resultados, edición y aprobación; definir esquemas y errores; registrar versión 0.1.0 y enlaces en CONTRACTS. Separar schema_version de result_version y dejar parámetros abiertos identificados.

**Criterios de aceptación:**

- **Given** un resultado con versión de esquema y de contenido, **When** se valida, **Then** ambas versiones son independientes y los campos obligatorios están presentes.
- **Given** una carga sin consent_reference, **When** se valida, **Then** se identifica invalid_consent_reference sin confundir referencia con evidencia.
- **Given** un cambio elimina un campo obligatorio, **When** se revisa compatibilidad, **Then** se exige versión mayor y migración.

**Tareas técnicas:**

1. Escribir OpenAPI y esquemas de objetos compartidos.
2. Definir invariantes de referencias y matriz operación/error.
3. Registrar contrato y ejemplos sin fijar 24 h en el esquema.

**Pruebas y evidencia:** validación de esquemas, referencias y ejemplos; no requiere runtime. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** —.

**Dependencias de integración/cierre:** —.

**Estimación:** 1–2; límites y autorización pendientes pueden impedir cierre jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01 a RF-05; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba; tasks existente §1.

### US-002 — Conformidad API

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: producir casos reutilizables de conformidad API, sin implementar endpoints.

**Contexto y objetivo:** cubre RF-01, RF-04, RF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** Construir solicitudes y respuestas sintéticas por operación; registrar precondiciones de identidad y pertenencia. Cubrir carga, permisos, conflictos y errores seguros sin declarar ejecutado un backend inexistente.

**Criterios de aceptación:**

- **Given** misma clave y mismo contenido, **When** se evalúa el caso de reenvío, **Then** se esperan los identificadores originales.
- **Given** misma clave con distinto contenido, **When** se evalúa la colisión, **Then** se espera 409 sin sustitución.
- **Given** identidad caducada o clase ajena, **When** se evalúa acceso, **Then** se espera 401 o denegación sin datos según contrato.

**Tareas técnicas:**

1. Crear fixtures multipart y respuestas 202/409/413/415/422.
2. Añadir casos sin consentimiento y con participantes duplicados.
3. Documentar correspondencia escenario-fixture y ejecutor futuro.

**Pruebas y evidencia:** contrato de payloads positivos/negativos y matriz de permisos. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001.

**Dependencias de integración/cierre:** 001.

**Estimación:** 0,5–1 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01, RF-04, RF-05; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba; tasks existente §2.

### US-003 — Conformidad de inferencia

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: definir entradas y salidas de prueba para adaptadores de IA sin exigir un modelo concreto.

**Contexto y objetivo:** cubre RF-02, RF-03; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0003.

**Flujo, reglas y límites:** Crear resultados completos y por etapa, incluidos hablantes sin asignar y categorías vacías. Separar conformidad estructural de evaluación lingüística/pedagógica.

**Criterios de aceptación:**

- **Given** hablante de sesión sin nombre, **When** se valida su resultado, **Then** participant_id nullable es aceptado.
- **Given** segmento con fin anterior al inicio, **When** se valida, **Then** falla la invariante temporal.
- **Given** ítem de categoría desconocida o speaker_id inexistente, **When** se valida, **Then** se rechaza y se identifica la referencia inválida.

**Tareas técnicas:**

1. Crear corpus JSON mínimo de transcripción y análisis.
2. Añadir mutaciones inválidas de intervalos, categorías y referencias.
3. Registrar qué no prueba el validador sobre fidelidad del contenido.

**Pruebas y evidencia:** contrato de resultados y validadores de invariantes. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001.

**Dependencias de integración/cierre:** 001.

**Estimación:** 0,5–1 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-02, RF-03; ARCHITECTURE; ADR-0003 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba; tasks existente §3.

### US-004 — Conformidad de interfaz

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: proporcionar ejemplos de contrato que pueda consumir el cliente React/TypeScript antes de existir la API.

**Contexto y objetivo:** cubre RF-04, RF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** Preparar payloads REST de espera, fallo, borrador, corrección y publicación; cada transición conserva clase y versión. Los ejemplos deben poder validarse tanto contra el contrato como contra los tipos del cliente TypeScript, sin decidir todavía si esos tipos se generan o mantienen manualmente. No diseñar la regla pendiente de revisión incompleta.

**Criterios de aceptación:**

- **Given** borrador en versión 1, **When** se construye vista de estudiante, **Then** el caso no entrega transcript ni analysis.
- **Given** corrección válida, **When** se construye siguiente respuesta, **Then** versión 2 queda in_review sin publicación.
- **Given** aprobación válida de versión 2, **When** se prepara respuesta, **Then** esa versión figura published y consultable.
- **Given** un error REST documentado, **When** el cliente TypeScript interpreta su payload, **Then** puede distinguir código, reintentabilidad y mensaje seguro sin depender de campos no definidos.

**Tareas técnicas:**

1. Crear fixtures JSON y multipart por rol alineados con OpenAPI y los ejemplos compartidos.
2. Comprobar que los payloads válidos e inválidos pueden representarse con los tipos del cliente TypeScript sin ampliar el contrato de forma implícita.
3. Incluir espera, fallo, error 409, recarga de versión, aprobación y vencimiento sin revisión con plazo variable; anotar el caso pendiente de Lay sin expectativa inventada.

**Pruebas y evidencia:** validación de contrato, compatibilidad de tipos del cliente y consistencia temporal de fixtures, sin pruebas visuales aún. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001.

**Dependencias de integración/cierre:** 001.

**Estimación:** 0,5–1 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores; dejar fixtures reutilizables por las pruebas del cliente React sin divergencias respecto al contrato; completar las pruebas indicadas y el DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-04, RF-05; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba; tasks existente §4.

### US-005 — Integración del contrato

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: comprobar que los tres conjuntos de fixtures comparten un único contrato.

**Contexto y objetivo:** cubre RF-01 a RF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** Reunir casos API, IA y cliente; ejecutar validación común; registrar cobertura de cada escenario de la spec y carencias. No afirmar implementación funcional por pasar fixtures.

**Criterios de aceptación:**

- **Given** tres conjuntos de fixtures, **When** se validan juntos, **Then** todos usan las mismas claves, estados y versión.
- **Given** un fixture referencia otra clase, **When** se comprueba consistencia, **Then** la comprobación falla y localiza el caso.
- **Given** un escenario de la spec no tiene fixture, **When** se genera matriz, **Then** se señala como pendiente y no se cierra integración.

**Tareas técnicas:**

1. Unificar ejecución de validadores.
2. Construir matriz spec-fixture-evidencia.
3. Preparar informe de conformidad y verificación completa del cambio.

**Pruebas y evidencia:** contrato transversal y comprobación de enlaces. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 002,003,004.

**Dependencias de integración/cierre:** 001,002,003,004.

**Estimación:** 0,5–1 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01 a RF-05; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba; tasks existente §5.

### US-006 — Skeleton desplegado

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como operador, quiero arrancar y desplegar el servicio mínimo en pruebas y producción para detectar pronto fallos de entorno.

**Contexto y objetivo:** cubre RNF-03; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** Crear API, worker y mantenimiento con entradas separadas y cliente mínimo. Conectar salud y un recorrido sintético declarado; configurar entornos aislados sin datos reales. No incluir modelos ni funcionalidades RF como si estuvieran implementadas.

**Criterios de aceptación:**

- **Given** clon con variables documentadas, **When** se arranca por Make, **Then** cliente y servicios responden y conectan.
- **Given** DB inaccesible, **When** se consulta disponibilidad, **Then** se informa dependencia caída sin credenciales.
- **Given** dos entornos desplegados, **When** se inspeccionan volúmenes y secretos, **Then** no comparten datos ni credenciales.

**Tareas técnicas:**

1. Crear estructura y puntos de salud.
2. Añadir Makefiles, Dockerfiles, tres Compose y env.example según CONTRIBUTING.
3. Documentar y ensayar despliegue y reversión de versión mínima.

**Pruebas y evidencia:** smoke local con/sin Docker y smoke de ambos entornos. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001 y ADR-0001/0002; host y permisos.

**Dependencias de integración/cierre:** 001.

**Estimación:** 2–4; infraestructura no disponible bloquea cierre jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RNF-03; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-007 — CI e integración del skeleton

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: ejecutar checks reproducibles del skeleton y verificar su integración desplegada.

**Contexto y objetivo:** cubre RNF-03; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** Conectar objetivos de cada servicio a make ci, incluyendo lint, tests CPU y construcción de producción. Recorrer instalación documentada en Windows/Git Bash y entorno servidor acordado; no exigir GPU al CI público.

**Criterios de aceptación:**

- **Given** un test falla, **When** se ejecuta make ci, **Then** sale con error.
- **Given** servicios mínimos sanos, **When** se ejecuta smoke desplegado, **Then** cliente llega a API y al recorrido simulado.
- **Given** se construye imagen de producción, **When** se inspecciona configuración, **Then** no contiene secretos ni audios.

**Tareas técnicas:**

1. Configurar checks por servicio.
2. Conectar CI existente sin desactivar Convenciones/OpenSpec.
3. Ejecutar matriz de arranque y documentar diagnóstico de fallos.

**Pruebas y evidencia:** CI CPU, construcción y smoke de despliegue. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 006.

**Dependencias de integración/cierre:** 006.

**Estimación:** 1–2 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RNF-03; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-008 — Carga durable e idempotente

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como emisor autorizado de CoTeach, quiero cargar audio una sola vez para obtener un trabajo durable que pueda consultar.

**Contexto y objetivo:** cubre RF-01, RD-02; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0002.

**Flujo, reglas y límites:** Autenticar emisor y pertenencia antes de aceptar; comprobar contenido, tamaño/formato y metadatos; guardar audio privado y trabajo; responder 202 tras persistencia. Limpiar temporales en fallo. Referencia válida no demuestra consentimiento real.

**Criterios de aceptación:**

- **Given** carga válida, **When** termina persistencia, **Then** 202 identifica clase y trabajo consultables.
- **Given** se repite clave con idéntico contenido, **When** se reenvía, **Then** no duplica trabajo.
- **Given** falta referencia o participantes se duplican, **When** se valida, **Then** 422 y ningún trabajo.
- **Given** almacenamiento falla antes de confirmar, **When** se carga, **Then** no devuelve 202 ni deja temporal sin limpieza.

**Tareas técnicas:**

1. Implementar recepción por streaming y límites acordados.
2. Crear persistencia atómica lógica audio/trabajo e idempotencia por emisor.
3. Integrar autenticación/política de acceso compartida y limpieza de huérfanos.

**Pruebas y evidencia:** unitarias de metadatos; integración real DB/almacenamiento; reenvíos concurrentes y fallos parciales. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001,006; límites y contrato de identidad.

**Dependencias de integración/cierre:** 005,007; verificación de seguridad en 016 y consentimiento real en 023 para uso real.

**Estimación:** 3–5; alta incertidumbre por consistencia entre archivo y DB jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01, RD-02; ARCHITECTURE; ADR-0002 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-009 — Ejecución y recuperación de trabajos

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como operador, quiero recuperar trabajos interrumpidos sin duplicar resultados para mantener el procesamiento diferido.

**Contexto y objetivo:** cubre RF-01, RNF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0002.

**Flujo, reglas y límites:** Reclamar trabajo con exclusión mutua; persistir etapa e intento; procesar fuera de transacción larga; reintentar solo fallos transitorios con límite acordado. Expiración invalida fuente y escrituras tardías.

**Criterios de aceptación:**

- **Given** dos trabajadores compiten, **When** reclaman un trabajo, **Then** solo el intento vigente puede persistir resultado.
- **Given** un trabajador pierde su lease, **When** intenta guardar después de recuperación, **Then** se rechaza escritura tardía.
- **Given** fallo transitorio, **When** se reintenta, **Then** conserva última etapa válida y contador.
- **Given** audio expirado, **When** se recupera trabajo, **Then** no inicia inferencia con copia retenida.

**Tareas técnicas:**

1. Implementar reclamación, heartbeat y token según ADR aprobado.
2. Persistir checkpoints y clasificación de errores.
3. Añadir recuperador independiente e invalidación por expiración.

**Pruebas y evidencia:** integración concurrente DB, reinicio forzado, doble entrega y reloj controlado. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001,006; ADR-0002.

**Dependencias de integración/cierre:** 008,007.

**Estimación:** 3–5; necesita validar diseño de concurrencia jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01, RNF-05; ARCHITECTURE; ADR-0002 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-010 — Integración de recepción

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: verificar recepción y recuperación con API, DB y almacenamiento reales.

**Contexto y objetivo:** cubre RF-01, RNF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0002.

**Flujo, reglas y límites:** Enviar cargas de prueba y consultar trabajos con identidad autorizada; inyectar interrupción tras almacenamiento y durante ejecución. Worker simulado aquí verifica orquestación, no RF-02/03.

**Criterios de aceptación:**

- **Given** carga aceptada, **When** se reinicia API, **Then** trabajo sigue consultable.
- **Given** se corta conexión tras aceptar, **When** cliente repite clave, **Then** recupera referencias originales.
- **Given** almacenamiento falla, **When** se revisa estado tras limpieza, **Then** no queda trabajo aceptado sin fuente válida.

**Tareas técnicas:**

1. Preparar entorno real aislado y audio sintético.
2. Automatizar fallos de recepción y reinicio.
3. Verificar errores de job y ausencia de datos sensibles en logs.

**Pruebas y evidencia:** integración HTTP/DB/archivos y recuperación. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 008,009.

**Dependencias de integración/cierre:** 005,007,008,009.

**Estimación:** 1–2 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01, RNF-05; ARCHITECTURE; ADR-0002 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-011 — Transcripción normalizada

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como docente, quiero una transcripción con tiempos para revisar lo ocurrido en la clase.

**Contexto y objetivo:** cubre RF-02; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0003.

**Flujo, reglas y límites:** Decodificar audio admitido, normalizar sin alterar duración útil, ejecutar adaptador aprobado y producir segmentos con offsets del original. Medir calidad por idioma; silencio y corrupción requieren resultados explícitos acordados.

**Criterios de aceptación:**

- **Given** audio anotado en idioma acordado, **When** se transcribe, **Then** segmentos tienen tiempos válidos y se calcula WER/CER.
- **Given** audio corrupto, **When** se normaliza, **Then** falla con código seguro sin texto fabricado.
- **Given** modelo agota memoria, **When** se procesa, **Then** se registra fallo recuperable o terminal según política sin cambiar modelo silenciosamente.

**Tareas técnicas:**

1. Implementar normalización y limpieza temporal.
2. Adaptar transcriptor y registrar revisión/parámetros.
3. Preparar referencias anotadas y medir tiempos y memoria.

**Pruebas y evidencia:** unitarias de offsets; integración con modelo real; evaluación separada de CI. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001,006; ADR-0003 y equipo de ejecución.

**Dependencias de integración/cierre:** 003,007; idiomas y umbrales para aceptación de calidad.

**Estimación:** 2–4 tras disponibilidad de modelo; calidad no estimable sin muestras jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-02; ARCHITECTURE; ADR-0003 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-012 — Diarización e integración de hablantes

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como docente, quiero distinguir intervenciones y asociar manualmente voces para corregir atribuciones ambiguas.

**Contexto y objetivo:** cubre RF-02, RD-04; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0003.

**Flujo, reglas y límites:** Ejecutar diarización, cruzar intervalos con transcripción y conservar speaker_id de sesión. No equiparar número de voces con participantes ni inferir nombres por orden. Integrar salida con jobs; la edición de asociaciones pertenece a 017.

**Criterios de aceptación:**

- **Given** audio 1–1 y 1–4 anotado, **When** se diariza, **Then** se mide DER y atribución frente a referencia.
- **Given** participante permanece en silencio, **When** se cuentan voces, **Then** no se inventa una voz por cada nombre.
- **Given** hay solapamiento o asociación dudosa, **When** se genera resultado, **Then** no inventa identidad y admite asignación nula.

**Tareas técnicas:**

1. Evaluar acceso a pesos/licencias y compatibilidad.
2. Implementar cruce temporal y representación de ambigüedad conforme contrato.
3. Integrar etapa con token vigente y preparar evaluación de solapamientos.

**Pruebas y evidencia:** unitarias de intervalos; modelo real con ruido/silencio/solapamiento; integración job-transcripción. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001,006; ADR-0003 y hardware.

**Dependencias de integración/cierre:** 009,011; corpus y umbrales acordados.

**Estimación:** 4–7 o más; máxima incertidumbre, reestimar tras prueba corta jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-02, RD-04; ARCHITECTURE; ADR-0003 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-013 — Repaso y resumen general

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como docente, quiero un resumen general y repaso por categorías para preparar material de revisión.

**Contexto y objetivo:** cubre RF-03; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0003.

**Flujo, reglas y límites:** Procesar transcripción como datos, dividir entradas largas, extraer seis categorías del PRD y consolidar sin duplicados ni pérdida de contexto. Validar estructura y mantener categorías vacías cuando no exista evidencia; no añadir RF-06/07.

**Criterios de aceptación:**

- **Given** transcripción con vocabulario y correcciones, **When** se analiza, **Then** resultado separa categorías y resumen general.
- **Given** entrada excede contexto del modelo, **When** se fragmenta y consolida, **Then** se conserva cobertura de todos los fragmentos.
- **Given** transcripción contiene instrucciones maliciosas, **When** se procesa, **Then** no cambia permisos ni ejecuta acciones.

**Tareas técnicas:**

1. Crear adaptador y plantilla de extracción versionada.
2. Implementar fragmentación, consolidación y validación de salida.
3. Tratar JSON inválido como fallo de etapa con reintento limitado acordado.

**Pruebas y evidencia:** unitarias de consolidación; contrato de salida; inferencia real y pruebas de inyección como texto. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001,006; ADR-0003.

**Dependencias de integración/cierre:** 003,007; modelo y parámetros evaluados.

**Estimación:** 3–5; depende del contexto y calidad del modelo jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-03; ARCHITECTURE; ADR-0003 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-014 — Evaluación e integración pedagógica

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: evaluar fidelidad pedagógica y conectar transcripción/diarización con análisis real.

**Contexto y objetivo:** cubre RF-03, RNF-04; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0003.

**Flujo, reglas y límites:** Construir corpus con contenidos esperados y rúbrica acordada; comparar afirmaciones, omisiones y resumen con transcripción/audio. Verificar que salida estructuralmente válida no implica aprobación pedagógica.

**Criterios de aceptación:**

- **Given** JSON válido con afirmación sin respaldo, **When** se aplica rúbrica, **Then** se registra fallo de fidelidad.
- **Given** clase sin determinada categoría, **When** se evalúa, **Then** vacío justificado no se penaliza como contenido perdido.
- **Given** pipeline real completo, **When** se ejecuta corpus, **Then** se conserva trazabilidad de modelo, entrada y puntuación.

**Tareas técnicas:**

1. Acordar rúbrica con Lay/equipo y anotar muestras.
2. Conectar etapas reales y recoger métricas.
3. Documentar defectos de calidad y repetir evaluación tras correcciones.

**Pruebas y evidencia:** evaluación humana reproducible e integración de inferencia; no solo schema. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 012,013.

**Dependencias de integración/cierre:** 009,012,013; idiomas y umbrales Lay.

**Estimación:** 2–4 más disponibilidad de revisión de Lay jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-03, RNF-04; ARCHITECTURE; ADR-0003 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-015 — Persistencia y consulta de versiones

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como docente, quiero consultar resultados persistidos de mi clase para revisarlos sin perder versiones.

**Contexto y objetivo:** cubre RF-04; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0002.

**Flujo, reglas y límites:** Recibir salida completa validada, persistir versión y devolver transcript/analysis separados. Consultas repetidas no crean versiones. Estudiante solo recibe versión publicada; no fusionar borrador actual con publicación anterior.

**Criterios de aceptación:**

- **Given** resultado válido almacenado, **When** API reinicia y docente consulta, **Then** mismos identificadores, versión y contenido.
- **Given** resultado tiene speaker_id inexistente, **When** se persiste, **Then** no se marca completo ni publicable.
- **Given** alumno consulta clase sin publicación, **When** se resuelve visibilidad, **Then** no recibe borrador.

**Tareas técnicas:**

1. Crear migraciones y repositorio de versiones.
2. Implementar validación de referencias y persistencia transaccional.
3. Implementar consulta y resolver de versión visible usando política de acceso.

**Pruebas y evidencia:** integración DB real, rollback, reinicio y contrato de consultas. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001,006; ADR-0002.

**Dependencias de integración/cierre:** 005,007; matriz de seguridad 016 para integración pública.

**Estimación:** 3–5; migraciones y visibilidad requieren pruebas específicas jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-04; ARCHITECTURE; ADR-0002 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-016 — Integración de acceso por clase

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: integrar y comprobar autorización uniforme en las operaciones de clase.

**Contexto y objetivo:** cubre RF-04, RNF-01; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0004.

**Flujo, reglas y límites:** Conectar validación de identidad y pertenencia con carga, jobs, resultados, edición y aprobación disponibles. La política debe ser reutilizada desde 008/015, no añadida después; esta historia es auditoría e integración, no un backend alternativo de permisos.

**Criterios de aceptación:**

- **Given** token expirado, **When** se consulta job, **Then** 401 sin metadatos.
- **Given** alumno modifica role en JSON, **When** intenta editar, **Then** se deniega sin cambios.
- **Given** persona autenticada de otra clase, **When** consulta resultado o job, **Then** no descubre contenido ni existencia por respuesta.
- **Given** docente asignado, **When** consulta borrador, **Then** accede solo a sus clases.

**Tareas técnicas:**

1. Formalizar matriz emisor/docente/estudiante por operación.
2. Conectar emisor aprobado o emisor sintético aislado.
3. Ejecutar ataques de acceso transversal y revisar logs/cachés.

**Pruebas y evidencia:** integración de autenticación real de demo y pruebas negativas en cada endpoint; reejecutar en 019. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001 y diseño de identidad; código compartido con 008/015.

**Dependencias de integración/cierre:** 008,015; revisión de endpoints posteriores en 019/022.

**Estimación:** 2–4; integración de identidad externa no estimable sin contrato jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-04, RNF-01; ARCHITECTURE; ADR-0004 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-017 — Corrección docente versionada

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como docente asignado, quiero corregir texto, análisis y asociaciones antes de aprobar para evitar compartir errores.

**Contexto y objetivo:** cubre RF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0004.

**Flujo, reglas y límites:** Leer versión vigente; enviar solo cambios permitidos y expected_result_version; validar participantes y categorías; persistir nueva versión in_review. No editar permisos, clase, plazo ni publicación desde PATCH.

**Criterios de aceptación:**

- **Given** docente modifica resumen en versión vigente, **When** guarda, **Then** nueva versión conserva secciones no enviadas.
- **Given** dos docentes parten de versión 1, **When** el segundo guarda tras el primero, **Then** 409 sin sobrescritura.
- **Given** se asigna voz a participante de otra clase, **When** se valida, **Then** rechazo sin alterar versión.

**Tareas técnicas:**

1. Implementar servicio de revisión y lista de campos editables.
2. Aplicar control optimista y reglas de reemplazo acordadas.
3. Registrar autor y versión sin duplicar política de acceso.

**Pruebas y evidencia:** unitarias de cambios; integración concurrente DB; contrato PATCH. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001; interfaces de persistencia de 015 acordadas.

**Dependencias de integración/cierre:** 015,016; política de edición posterior pendiente Lay.

**Estimación:** 2–3; trabajo backend, no frontend jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-05; ARCHITECTURE; ADR-0004 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-018 — Aprobación y publicación programada

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como docente, quiero que mi aprobación publique la versión revisada; como estudiante, quiero acceder al resultado cuando se publique.

**Contexto y objetivo:** cubre RF-05, RD-06; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0004.

**Flujo, reglas y límites:** Unificar aprobación y vencimiento sin revisión en transición atómica idempotente. Capturar plazo configurable según política que se apruebe; mantener proceso independiente de GPU. No implementar regla de in_review vencido antes de confirmación.

**Criterios de aceptación:**

- **Given** versión vigente aprobada antes del plazo, **When** se confirma operación, **Then** esa versión queda publicada y accesible al alumnado autorizado.
- **Given** resultado válido pending vence, **When** actúa mantenimiento, **Then** publicación automática identifica esa versión.
- **Given** dos intentos de publicar concurren, **When** se confirman, **Then** una publicación sin duplicados ni versión obsoleta.

**Tareas técnicas:**

1. Implementar transición común de publicación.
2. Añadir endpoint approve con versión esperada.
3. Implementar consulta de vencidos y planificación parametrizada con reintentos.

**Pruebas y evidencia:** integración DB concurrente; reloj justo antes/en/después del vencimiento; repetición de aprobación. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001 y reglas de plazo acordadas; interfaz de versiones.

**Dependencias de integración/cierre:** 017,016; Lay: inicio, plazo, in_review y edición posterior.

**Estimación:** 2–4; política abierta bloquea cierre, no se inventa rama por defecto jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-05, RD-06; ARCHITECTURE; ADR-0004 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-019 — Integración de revisión y reloj

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: verificar revisión y publicación como una sola funcionalidad con reloj controlado.

**Contexto y objetivo:** cubre RF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0004.

**Flujo, reglas y límites:** Recorrer corrección, aprobación y consulta por estudiante; después probar otra clase sin revisión y vencimiento. Interrumpir mantenimiento y restaurarlo. El caso in_review vencido es decisión pendiente, no un escenario de aceptación que pase por estar bloqueado.

**Criterios de aceptación:**

- **Given** clase corregida y aprobada, **When** estudiante consulta, **Then** lee exactamente versión corregida.
- **Given** mantenimiento estuvo parado al vencer pending, **When** reinicia, **Then** publica una vez sin cambiar modo ni versión.
- **Given** versión antigua se aprueba, **When** se integra API/DB, **Then** 409 y publicación vigente intacta.

**Tareas técnicas:**

1. Automatizar secuencias con reloj inyectable.
2. Inyectar caída entre selección y confirmación.
3. Reejecutar matriz de permisos sobre PATCH/approve y verificar todas las secciones.

**Pruebas y evidencia:** integración real de revisión/planificador/consulta; concurrencia y recuperación. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 017,018.

**Dependencias de integración/cierre:** 015,016,017,018; decisión Lay sobre caso no cubierto.

**Estimación:** 1,5–3 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-05; ARCHITECTURE; ADR-0004 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-020 — Carga y seguimiento en la interfaz web React

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como docente autorizado, quiero enviar audio y seguir su progreso para saber cuándo puedo revisarlo.

**Contexto y objetivo:** cubre RF-01, RF-04; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** Seleccionar audio y metadatos en React; aplicar validaciones locales orientativas; enviar multipart a `POST /v1/classes` con una clave de idempotencia conservada; consultar `GET /v1/jobs/{job_id}` hasta un estado terminal; mostrar etapa y error seguro. El polling se detiene al desmontar la vista o alcanzar estado terminal. FastAPI conserva la autoridad sobre validación, identidad y permisos.

**Criterios de aceptación:**

- **Given** FastAPI devuelve 202, **When** el cliente React conserva class_id y job_id, **Then** muestra el trabajo y consulta su progreso sin reenviar el audio.
- **Given** respuesta se pierde, **When** docente reintenta misma carga, **Then** conserva clave de idempotencia.
- **Given** API devuelve 413 o 415, **When** se muestra error, **Then** explica límite/formato sin reintento infinito.
- **Given** la vista se desmonta o el trabajo alcanza un estado terminal, **When** existe polling activo, **Then** se cancela y no genera solicitudes REST adicionales.

**Tareas técnicas:**

1. Preparar la aplicación React con TypeScript y Vite y construir el formulario tipado de audio y metadatos.
2. Implementar el cliente REST multipart para `POST /v1/classes` y conservar identificadores y clave de idempotencia en el estado aislado de la sesión del navegador.
3. Implementar polling cancelable sobre `GET /v1/jobs/{job_id}` y tratar 401, 413, 415, 422 y errores transitorios sin reintentos ilimitados.

**Pruebas y evidencia:** comprobación de tipos, pruebas de componentes y del cliente REST con fixtures; construcción Vite de producción; integración real en 022. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001,004,006; React, TypeScript y Vite documentados en ADR-0001, todavía Propuesto.

**Dependencias de integración/cierre:** 007; 010 requerido para conexión real de 022.

**Estimación:** 1,5–3 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores; superar comprobación TypeScript y construcción Vite de producción; completar las pruebas indicadas y el DoD común. La integración de esta historia puede usar fixtures, pero US-022 no se considera completada con mocks. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01, RF-04; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-021 — Revisión docente y consulta en la interfaz web React

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como docente, quiero editar y aprobar el repaso; como estudiante, quiero leer únicamente la versión publicada de mi clase.

**Contexto y objetivo:** cubre RF-04, RF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** React consulta `GET /v1/classes/{class_id}/result` y muestra transcripción con voces y tiempos separada del análisis. El formulario docente envía `PATCH /v1/classes/{class_id}/review` con expected_result_version y la aprobación explícita usa `POST /v1/classes/{class_id}/approve`. La vista de estudiante es de solo lectura. El cliente limpia estado al cambiar identidad o clase y no comparte caché de resultados entre usuarios; FastAPI decide permisos y versión visible.

**Criterios de aceptación:**

- **Given** docente guarda corrección, **When** API devuelve nueva versión, **Then** UI actualiza versión antes de aprobar.
- **Given** API devuelve 409, **When** docente intenta guardar, **Then** UI informa conflicto y permite recargar sin sobrescribir.
- **Given** alumno autenticado consulta publicado, **When** se renderiza, **Then** ve contenido sin controles de edición ni borradores.
- **Given** cambia la identidad o la clase activa, **When** React actualiza la navegación, **Then** elimina del estado y la caché los resultados de la sesión anterior antes de solicitar otros.

**Tareas técnicas:**

1. Crear componentes TypeScript para transcripción, análisis y estados de revisión, mostrando acciones solo cuando la API autoriza el flujo correspondiente.
2. Implementar el cliente REST de consulta, edición de hablantes/análisis y aprobación con expected_result_version.
3. Implementar recarga tras 409, vista estudiantil de solo lectura y limpieza de estado/caché al cambiar identidad o clase.

**Pruebas y evidencia:** comprobación de tipos, pruebas de componentes y contrato del cliente REST, conflictos de versión y aislamiento de sesiones. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 004,020; contrato de revisión.

**Dependencias de integración/cierre:** 017,018 para conexión real; 022 verifica permisos extremo a extremo.

**Estimación:** 2–4 jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores; comprobar que ningún borrador aparece en la vista estudiantil y que React no decide permisos; superar comprobación TypeScript y construcción Vite; completar las pruebas indicadas y el DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-04, RF-05; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-022 — Integración E2E de React con FastAPI

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: demostrar el flujo completo del cliente React contra FastAPI y los servicios/modelos reales.

**Contexto y objetivo:** cubre RF-01 a RF-05; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0001.

**Flujo, reglas y límites:** Ejecutar la construcción React/Vite contra FastAPI mediante los endpoints REST existentes. Usar audio simulado permitido pero inferencia real; cargar, observar estados, corregir, aprobar y consultar desde una sesión de estudiante. Probar además publicación automática con reloj/plazo de ensayo identificado. No añadir endpoints exclusivos para la UI ni aceptar respuestas precalculadas como demo funcional.

**Criterios de aceptación:**

- **Given** audio nuevo y pipeline real, **When** docente completa recorrido y aprueba, **Then** estudiante autorizado ve versión corregida.
- **Given** otra clase no se revisa, **When** vence plazo de ensayo, **Then** estudiante ve publicación automática.
- **Given** sesión cambia a usuario ajeno, **When** se consulta mismo identificador, **Then** no recibe datos por API ni caché UI.
- **Given** la construcción de producción del frontend usa la URL configurada de FastAPI, **When** se ejecuta el recorrido E2E, **Then** todas las operaciones respetan los contratos REST versionados sin depender del servidor de desarrollo de Vite.

**Tareas técnicas:**

1. Configurar la construcción de producción de React/Vite y FastAPI sin mocks en la ruta demostrada, con origen de API configurable y política CORS restringida si los orígenes son distintos.
2. Automatizar el recorrido navegador–FastAPI con cuentas sintéticas aisladas y comprobar los límites de contrato en cada llamada REST.
3. Registrar evidencia de la construcción, del recorrido real y de los defectos bloqueantes de flujo, contrato y seguridad.

**Pruebas y evidencia:** E2E real navegador React/FastAPI/DB/almacenamiento/modelos, verificación del contrato REST y prueba negativa multiusuario. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 010,014,016,019,020,021,023.

**Dependencias de integración/cierre:** 010,014,016,019,020,021,023.

**Estimación:** 2–4 más correcciones; no estimable como medio día jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores desde la construcción de producción, sin mocks en el recorrido; superar comprobación TypeScript, construcción Vite y pruebas E2E; verificar errores REST seguros y ausencia de datos residuales entre sesiones; completar el DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01 a RF-05; ARCHITECTURE; ADR-0001 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-023 — Consentimiento, purga y aislamiento

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Como operador, quiero verificar autorización de uso del audio y eliminarlo a los 14 días para cumplir la retención acordada.

**Contexto y objetivo:** cubre RNF-01, RNF-02, RD-01, RD-02; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0004.

**Flujo, reglas y límites:** Separar referencia de consentimiento de comprobación de evidencia según política acordada. Calcular expiración desde recepción, bloquear lectura al vencer, eliminar original/temporales y evitar copias en backups. Purga debe coordinarse con trabajos activos y dejar auditoría sin contenido.

**Criterios de aceptación:**

- **Given** referencia bien formada sin evidencia válida, **When** se verifica antes de uso real, **Then** no se considera consentimiento acreditado.
- **Given** audio alcanza 14 días, **When** mantenimiento purga, **Then** original y temporales quedan eliminados y no se reprocesa.
- **Given** fallo de borrado, **When** se reintenta tras reinicio, **Then** permanece no accesible y el fallo es observable.
- **Given** backup se restaura, **When** se inspecciona contenido, **Then** no reaparecen audios vencidos.

**Tareas técnicas:**

1. Integrar comprobador de evidencia acordado.
2. Implementar expiración, borrado reintentable e invalidación de trabajos.
3. Verificar exclusión de backups, permisos de archivos y saneamiento de logs.

**Pruebas y evidencia:** reloj controlado en frontera 14 días; fallos de archivo; trabajador concurrente; restauración y revisión de logs. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 001,006; política de consentimiento para ruta real.

**Dependencias de integración/cierre:** 008,009,016; ADR-0004, evidencia de consentimiento y política de copias.

**Estimación:** 3–6; seguridad y almacenamiento requieren revisión cruzada jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RNF-01, RNF-02, RD-01, RD-02; ARCHITECTURE; ADR-0004 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

### US-024 — Ensayo E2E y capacidad de entrega

**Épica, responsable, labels, prioridad e hito:** tabla resumen; propuesta sin asignación.

**Historia / objetivo técnico:** Especificación técnica: cerrar evidencias de capacidad, operación y entrega tras un ensayo funcional previo a la demo.

**Contexto y objetivo:** cubre RF-01 a RF-05, RNF-03, RNF-04; entrega exclusivamente este incremento. No implementa las responsabilidades de historias dependientes ni aprueba el ADR-0003.

**Flujo, reglas y límites:** Antes del 11/12 ensayar ruta real de 022 y recuperación básica. Para el 15/12 completar lote representativo de diez clases, métricas por etapa, guía de operación y restauración; no extrapolar diez clases diarias desde clips cortos.

**Criterios de aceptación:**

- **Given** corpus representativo autorizado o simulado, **When** se procesa lote de diez, **Then** informe registra duraciones, hardware, memoria, fallos y límites.
- **Given** GPU deja de estar disponible, **When** se ensaya contingencia, **Then** se informa indisponibilidad sin presentar fixtures como ejecución real.
- **Given** operador sigue guía en entorno limpio, **When** restaura versión y DB, **Then** recupera servicio sin restaurar audio vencido.

**Tareas técnicas:**

1. Preparar guion y evidencia de ensayo previo a demo.
2. Ejecutar lote y recopilar métricas/licencias sin datos personales.
3. Completar runbook de recuperación, purga y límites con revisión de las tres personas.

**Pruebas y evidencia:** E2E de entrega, carga representativa y restauración; evaluación GPU fuera de CI público. Conservar entrada sintética, resultado esperado y observado.

**Dependencias de inicio:** 014,022,023 para ejecución; guion puede redactarse antes.

**Dependencias de integración/cierre:** 014,022,023 y todas las historias previas cerradas.

**Estimación:** 3–5 más tiempo de cómputo; capacidad depende de duración real del corpus jornadas-persona.

**DoD específico:** demostrar todos los escenarios anteriores y completar las pruebas indicadas, además del DoD común. Una decisión pendiente que cambie las expectativas impide cerrar la historia; no cuenta como criterio superado.

**Referencias:** PRD RF-01 a RF-05, RNF-03, RNF-04; ARCHITECTURE; ADR-0003 (Propuesto); mvp-service-contracts y agrupación OpenSpec indicada arriba (spec funcional pendiente).

## Decisiones y reglas pendientes

Lay: idiomas y rúbrica/umbrales de calidad; formatos y muestras; consentimiento y responsable de verificarlo (recibir consent_reference no prueba consentimiento); plazo provisional configurable de 24 h, inicio del cómputo, revisión iniciada sin aprobar al vencer y edición tras publicación; retención de derivados. US-018/019 no implementarán una política de revisión incompleta inventada. Aprobar una versión vigente debe publicarla efectivamente; alumnado solo consulta publicado. US-023 requiere acordar evidencia de consentimiento antes de procesar audio real.

Equipo: aprobar formalmente los ADR-0001–0004; React, TypeScript y Vite quedan documentados como cliente web propuesto y FastAPI como backend; siguen pendientes recursos/GPU y presupuesto privado, entorno de producción y credenciales, contrato de identidad, límites de carga/reintentos y exclusión de audios de backups. El origen del plazo y los detalles de persistencia de la arquitectura siguen siendo propuestas. Los permisos se resuelven en FastAPI, nunca por estado, nombres o roles enviados por React. Software libre requiere revisar bibliotecas y pesos por separado.

## Secuencia, reparto y riesgos

1. **Contrato y entorno (objetivo 23–26/11):** 001 → 002/003/004 → 005. 006 puede comenzar con contrato y elecciones técnicas aprobados sin esperar todos los fixtures; 007 integra el skeleton en ambos entornos. Seguridad compartida se diseña desde 001 y aplica desde 008/015; 016 comprueba su integración.
2. **Productores y consumidores (26/11–03/12, condicionado):** A trabaja 008/009/015; B evalúa hardware y 011/012, prepara 013 con transcripciones sintéticas; C aborda 002/005/007/010 y 020/021. 015 ya no espera 009: puede persistir fixtures. 017 puede prepararse contra interfaz de repositorio acordada, pero no cerrar sin persistencia y permisos.
3. **Flujo y protección (04–08/12):** A integra 016/018/023; B completa 013/014; C completa 017/019/021. Purga y consentimiento se preparan desde el principio: 023 no es opcional.
4. **Puerta de demo (09–10/12):** 022 requiere explícitamente 014 (pipeline real), 023 (protección), revisión, acceso e interfaz integrados. Ensayo inicial de 024 antes del 11/12. Recorrido real de audio a revisión/publicación y consulta, más vencimiento sin revisión con reloj de ensayo identificado. Audio simulado es válido; inferencia simulada no acredita RF-02/03.
5. **Entrega (12–15/12):** cerrar 024 con lote representativo, métricas y guía de recuperación. No aplazar permisos, purga ni RF-01–05 a esta fase.

**Reparto provisional por carga:** A conserva 8 historias (001,006,008,009,015,016,018,023); B 5 (003,011–014); C 11 (002,004,005,007,010,017,019–022,024). Se trasladan 002 de A a C y coordinación de 024 de B a C. B aporta evaluación y métricas; A valida recuperación. 017 es backend aunque lo asuma C: confirmar esa competencia. A concentra transacciones/seguridad, B incertidumbre de modelos y C más pruebas pequeñas. El conteo no demuestra equilibrio.

C puede preparar pruebas de reloj y permisos de 023 para aliviar A; A revisa transacciones de 017 y B inferencia real de 022. Un propietario por historia, con interfaces y responsabilidades acordadas antes de editar. No añadir infraestructura a B hasta validar diarización.

**Viabilidad:** los rangos revisados son aproximadamente 44–80 jornadas-persona, más esperas y revisiones; sustituyen el rango anterior, demasiado optimista. Tres personas a tiempo completo disponen de unas 42 jornadas laborables entre 23/11 y 10/12, antes de festivos y ausencias. No hay fundamento para garantizar la demo: confirmar dedicación y experiencia, hacer benchmark temprano y replanificar con el equipo si no cabe. No recortar RF ni dar por completados mocks para ajustar el calendario.

**Bloqueos de Lay:** idiomas y calidad mínima; evidencia de consentimiento/responsable; 24 horas provisional, inicio del cómputo, revisión iniciada sin aprobar al vencer y edición posterior; retención de derivados. No convertir la propuesta conservadora del ADR sobre in_review en regla aprobada. Equipo/CoTeach deben acordar emisor de identidad, recursos, host, licencias, presupuesto, límites y backups.

**Riesgos:** diarización con solapamientos y cambios de idioma, acceso a pesos/GPU, contenido pedagógico inventado, fallos de consistencia DB/archivos y calendario sin holgura. Evaluar pronto corpus 1–1 y 1–4, medir tiempo y memoria, reservar revisión de Lay y probar concurrencia antes del E2E. No extrapolar diez clases/día desde clips cortos. Si GPU falla, comunicar indisponibilidad; un resultado precalculado identificado puede apoyar explicación pero no sustituye evidencia de demo funcional.

## Coherencia y publicación posterior

Se conservan ocho épicas y 24 IDs. US-001–005 mantienen correspondencia con las cinco secciones existentes de add-shared-mvp-contracts. El resto necesita specs funcionales y tasks aprobados. Integraciones 005,007,010,012,014,016,019,022,024 cierran sus agrupaciones y dependen de todas sus secciones. Los cambios referencian el contrato común; cualquier interfaz nueva debe especificarse antes de implementar, sin copiar contratos.

La aprobación docente publica efectivamente; una referencia no demuestra consentimiento; validar estructura no demuestra calidad pedagógica. RF-06/07 siguen fuera. in_review vencido sigue sin regla decidida.

Se conservan labels locales. area:* y scope:mvp son propuestas nuevas pendientes de aprobación y comprobación remota; no duplicar estados Kanban ni bloqueos nativos mediante labels. Este encargo no crea Issues ni modifica artefactos OpenSpec. Tras revisión: cerrar fase 1/ROADMAP, aprobar planes funcionales, comprobar Project/labels y autorizar publicación. Las Issues enlazarán tasks.md según plantilla; este catálogo no será fuente de avance.

