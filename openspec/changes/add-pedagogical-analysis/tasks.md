# Tasks

Plan de la funcionalidad `add-pedagogical-analysis` (E4, épica #4). La evaluación preliminar y la web pueden empezar sin esperar a E3; el adaptador del worker espera la interfaz de #55 y una selección explícita basada en la evaluación. La última sección integra E4 solo después de E3.

## 1. Evaluación preliminar de candidatos de análisis (inferencia)

**Criterios de aceptación:**

- Existe un conjunto versionado de transcripciones exclusivamente sintéticas y una rúbrica humana que cubren resumen, las seis categorías, omisiones y afirmaciones inventadas, sin datos personales ni contenido de clases.
- Se pueden ejecutar candidatos intercambiables sobre ese conjunto y registrar versión/revisión, configuración, estructura contractual, latencia y memoria.
- La evidencia compara candidatos y solicita una decisión del equipo; no fija ni selecciona automáticamente modelo, hardware, idioma ni umbral pedagógico.

**Depende de:** —

- [ ] 1.1 Definir las transcripciones sintéticas y la rúbrica de revisión humana para resumen y las seis categorías, y verificar mediante tests que no contienen datos de clase ni valores fuera del contrato.
- [ ] 1.2 Implementar el ejecutor de evaluación de candidatos desacoplado del worker, con dobles para tests y captura de versión, configuración, validez, latencia y memoria; verificar sus pruebas unitarias sin descargar modelos.
- [ ] 1.3 Documentar un formato de informe reproducible, ejecutar al menos una evaluación preliminar permitida y registrar sus limitaciones y la decisión requerida, verificando que no versiona textos ni audio reales.

## 2. Generación y validación del análisis en el worker (backend)

**Criterios de aceptación:**

- Tras una decisión explícita sobre candidato, el adaptador de análisis recibe la transcripción de E3 y devuelve únicamente un `Analysis` válido del contrato v0.2.0 con resumen y las seis categorías posibles, incluso cuando deba fragmentar una entrada larga y consolidarla sin duplicados.
- Las categorías sin hallazgos permanecen vacías; no hay fallback silencioso, contenido fijo ni resultado parcial si el modelo falla o entrega una estructura inválida.
- Los errores se integran con el procesamiento y reintentos de E3 sin publicar un resultado inválido.

**Depende de:** 1 y de la historia #55 de E3; la integración de errores se coordina con #58.

- [ ] 2.1 Tras la decisión aprobada del equipo, incorporar la dependencia y configuración local del candidato seleccionado siguiendo ADR-0003 o actualizar/crear el ADR si la elección lo exige; verificar carga sin red durante el procesamiento.
- [ ] 2.2 Implementar el adaptador de análisis sobre la interfaz `Analyzer` de #55, fragmentando transcripciones que excedan el contexto, consolidando todos los fragmentos sin duplicados y tratando las instrucciones maliciosas de la transcripción como datos; validar su salida como `Analysis` y verificar con transcripciones sintéticas los seis valores contractuales, listas vacías, identificadores únicos, cobertura de fragmentos e inyección de instrucciones.
- [ ] 2.3 **Depende de:** #58. Conectar el adaptador a la etapa `analyzing` sin modificar adaptadores de ASR o diarización, y cubrir con tests los fallos de modelo, salida inválida y ausencia de resultado persistido/publicable conforme a la política de #58.
- [ ] 2.4 Documentar la configuración, licencia/revisión del modelo seleccionado y la medición técnica correspondiente sin incluir datos de clases; verificar los comandos documentados en el equipo autorizado.

## 3. Presentación del repaso pedagógico (frontend)

**Criterios de aceptación:**

- La vista de resultado muestra primero el resumen general y presenta de forma localizada las seis categorías contractuales, reutilizando tokens y componentes de #66.
- Una categoría sin elementos tiene un estado vacío claro; los errores de consulta, autorización, revisión y publicación siguen con su tratamiento actual.
- Escritorio, tableta y móvil conservan contraste AA, orden semántico y navegación por teclado; los escenarios de MSW son exclusivamente sintéticos y conformes al contrato.

**Depende de:** —

- [ ] 3.1 Diseñar e implementar los componentes presentacionales de resumen, categorías e ítems reutilizando el sistema de diseño existente; verificar sus pruebas unitarias, etiquetas accesibles y orden de teclado.
- [ ] 3.2 Integrar la composición en la vista de resultado sin alterar autorización, rutas, caché de sesión, transcripción ni controles de E5; verificar en pruebas de integración de React la agrupación, localización y estados vacíos.
- [ ] 3.3 Ampliar los escenarios MSW con análisis sintéticos de varias y ninguna categoría, y verificar que el cliente usa sin cambios `backend/openapi.json` y que no aparecen datos de capacidades fuera del MVP.
- [ ] 3.4 Verificar responsividad y contraste de la composición de análisis en escritorio, tableta y móvil mediante las pruebas o comprobaciones del frontend establecidas en el repositorio.

## 4. Integración y evidencia de repaso pedagógico (integración)

**Criterios de aceptación:**

- Una grabación autorizada o simulada recorre E2, E3 y E4 hasta devolver una transcripción y un análisis válido con resumen y categorías; la web lo muestra según el contrato.
- La evidencia de la demostración distingue las pruebas técnicas de la revisión pedagógica humana y registra recursos, resultados y limitaciones sin publicar contenido de clase.
- Las regresiones de autorización, contratos, transcripción, reintentos y presentación existente continúan superándose.

**Depende de:** 1, 2, 3, las historias #55, #56, #57, #58 y #60 de E3.

- [ ] 4.1 Ejecutar el recorrido integrado audio → transcripción → análisis → consulta web con una entrada permitida y verificar resultado contractual, seis categorías posibles y estados de fallo sin resultado parcial.
- [ ] 4.2 Aplicar la rúbrica humana a la evidencia de integración, registrar cobertura, precisión cualitativa, omisiones, afirmaciones inventadas, latencia y memoria, y documentar límites para la demo sin declarar umbrales no aprobados.
- [ ] 4.3 Ejecutar las validaciones de backend, frontend, contrato y OpenSpec aplicables, y comprobar regresiones de acceso y publicación existentes antes de la revisión independiente.
- [ ] 4.4 Ejecutar `openspec validate add-pedagogical-analysis --strict` y la revisión independiente del cambio completo; corregir hallazgos dentro de alcance antes de sincronizar y archivar en el PR de integración.

## Workflow follow-up

- Tras la aprobación humana de este plan, crear las Issues desde estas cuatro secciones, añadir sus números y bloqueos, y enlazar `add-pedagogical-analysis` en `docs/ROADMAP.md` conforme a WORKFLOW §5.
- El PR de la sección 4 sincroniza las specs y archiva el cambio después de la revisión humana y del CI; no se archiva durante las historias 1 a 3.
