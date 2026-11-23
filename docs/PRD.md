# PRD

> Qué producto se construye, para quién y qué debe hacer: visión, objetivos, alcance, requisitos y decisiones de producto. Mapa de documentación: [WORKFLOW](../WORKFLOW.md#2-mapa-de-documentación).

- **Nombre:** CoTeach-AI
- **Responsable:** CoTeach, como entidad colaboradora y cliente; equipo del proyecto para el desarrollo del MVP.
- **Estado del documento:** Borrador

## 1. Resumen

CoTeach-AI es un servicio independiente de inteligencia artificial para clases particulares de idiomas. Recibe por API una grabación de clase, produce una transcripción diarizada y un repaso pedagógico estructurado, y entrega ambos resultados para su futura integración con CoTeach. El MVP debe demostrar el flujo completo en la presentación de diciembre, sin sustituir el criterio ni la revisión del profesorado.

## 2. Problema y oportunidad

- **Problema:** el contenido relevante de una clase grabada queda disperso en el audio y no puede reutilizarse fácilmente para el repaso; convertirlo manualmente en una transcripción y material de aprendizaje añade carga al profesorado.
- **Oportunidad:** transformar grabaciones consentidas en recursos trazables y estructurados permite que alumnado y profesorado revisen la sesión y sus aprendizajes sin depender de plataformas cerradas ni desplazar la labor docente.

## 3. Usuarios y partes interesadas

- **Usuarios:** profesorado de idiomas, que necesita revisar y compartir el resultado de una clase; alumnado, que necesita consultar la transcripción y el repaso posterior.
- **Partes interesadas:** CoTeach, entidad colaboradora y futura mantenedora; el equipo del proyecto, responsable de entregar el MVP; y Lay, interlocutora que ha confirmado los requisitos documentados en `docs/references/RESPUESTAS_LAY.md`.

## 4. Objetivos y criterios de éxito

| ID | Objetivo | Cómo se comprueba |
|---|---|---|
| OBJ-1 | Demostrar en diciembre un flujo completo desde una grabación de clase hasta resultados estructurados de repaso. | Una demostración procesa una grabación autorizada y muestra la transcripción diarizada, el análisis pedagógico y el resumen general resultantes. |
| OBJ-2 | Facilitar el repaso de una sesión sin aumentar la carga manual del profesorado. | El resultado separa la transcripción del repaso pedagógico, permite su revisión docente y se comparte según la regla de publicación aplicable. |
| OBJ-3 | Proteger datos educativos y de voz desde el diseño. | El audio original se purga automáticamente a los 14 días y las pruebas no publican datos personales o sensibles en el repositorio. |
| OBJ-4 | Mantener una base alineada con software libre, soberanía tecnológica y eficiencia computacional. | Las decisiones posteriores de producto y tecnología justifican su alineación con esos principios y documentan sus compromisos. |
| OBJ-5 | Preparar el servicio para una primera carga estimada de diez clases diarias y su evolución. | El MVP acepta y procesa lotes de prueba representativos de esa carga; las limitaciones observadas quedan documentadas. |

## 5. Principios de decisión

1. **El profesorado conserva el control:** la IA ayuda a preparar el repaso; no sustituye su criterio.
2. **Privacidad por diseño:** solo se procesan grabaciones consentidas o datos de prueba apropiados y se limita la conservación del audio.
3. **Trazabilidad antes que apariencia:** los resultados pedagógicos deben poder relacionarse con la sesión de origen cuando sea útil.
4. **Software libre y soberanía tecnológica:** se priorizan soluciones abiertas, interoperables y que eviten dependencias innecesarias.
5. **Flujo completo antes que amplitud:** para diciembre se prioriza una demostración funcional de extremo a extremo sobre funcionalidades adicionales.
6. **Eficiencia responsable:** el consumo computacional es un criterio de evaluación junto con calidad y privacidad.

## 6. Alcance

### Incluido

**Confirmado por Lay para el MVP:**

- Un servicio independiente y desacoplado de CoTeach que recibe por API un archivo de audio comprimido; la integración posterior con CoTeach se hará mediante esa API.
- Procesamiento diferido, no en tiempo real, de clases individuales y grupales de las modalidades 1–1 y 1–4.
- Transcripción con separación de intervenciones y marcas temporales; la API podrá recibir el número de participantes y sus nombres para asociarlos a las personas hablantes.
- Repaso pedagógico estructurado a partir de la transcripción: vocabulario, gramática y construcciones, errores y correcciones, aciertos reforzados, explicaciones o conceptos clave y dudas resueltas.
- Resultados estructurados que contengan transcripción y repaso, preparados para su consulta e integración futura.
- Conservación del audio original durante dos semanas y acceso previsto para profesorado y alumnado.
- Uso de software libre, privacidad por diseño, soberanía tecnológica y consideración del impacto ecológico.

**Funcionalidades deseables confirmadas, no imprescindibles mientras no se aprueben para la demostración:**

- Una presentación visual del MVP; Lay ha dado conformidad a mostrarla, sin fijar una tecnología de interfaz.

**Alcance aprobado para el MVP, con una regla provisional pendiente de validación por Lay:**

- Revisión y corrección de resultados por el profesorado antes de compartirlos. Si no hay revisión, los resultados se publican automáticamente al alumnado autorizado al transcurrir el plazo configurable de 24 horas.

### Fuera de alcance

- Transcripción o resultados en tiempo real.
- Reconocimiento automático de una misma persona entre sesiones distintas.
- Atención a menores en esta fase.
- Sustituir Odoo en sus funciones administrativas, de usuarios, reservas, pagos o emisión de tokens.
- Convertir el prototipo o los mockups actuales de CoTeach en la interfaz definitiva.

### Futuro

- Ampliar la capacidad más allá de la primera estimación de diez clases diarias.
- Incorporar resúmenes individualizados para alumnado de clases grupales y referencias temporales en elementos del análisis pedagógico.
- Incorporar más idiomas y otras funcionalidades de aprendizaje personalizado.
- Automatizar, si resulta viable y aprobado, la asociación de participantes entre sesiones.
- Integrar el servicio con la plataforma CoTeach cuando se disponga de su documentación técnica estable.

## 7. Glosario

| Término | Definición |
|---|---|
| Clase | Sesión particular de idiomas, individual o grupal, cuyo audio se procesa después de finalizar. |
| Transcripción diarizada | Transcripción con intervenciones separadas por persona hablante y marcas temporales. |
| Repaso pedagógico | Resultado estructurado que identifica aprendizajes, correcciones, aciertos, conceptos y dudas de una clase. |
| Persona hablante | Participante cuyas intervenciones se distinguen en la transcripción. |
| Audio original | Archivo de audio comprimido recibido por el servicio antes de su procesamiento. |

## 8. Flujos principales

1. **CoTeach/API → recepción:** el servicio recibe un audio comprimido, el número de participantes y, cuando estén disponibles, sus nombres.
2. **Servicio → transcripción:** procesa la sesión de forma diferida y produce una transcripción con intervenciones y marcas temporales.
3. **Servicio → análisis:** genera un análisis pedagógico y un resumen general de la clase a partir de la transcripción.
4. **Profesorado → revisión:** consulta, revisa o corrige los resultados y puede aprobar su compartición antes del plazo configurado.
5. **Alumnado autorizado → consulta:** accede a los resultados si el profesorado los aprueba o, si no hay revisión, cuando transcurre el plazo provisional configurable de 24 horas; el audio original se purga al cumplir 14 días de conservación.

## 9. Requisitos funcionales

### RF-01 — Recibir una grabación de clase mediante API

- **Objetivo:** OBJ-1, OBJ-5
- **Ámbito:** Base
- **Estado:** Confirmado por Lay

El sistema debe aceptar mediante API un archivo de audio comprimido de una clase, junto con el número de participantes y sus nombres cuando se proporcionen.

**Criterios de aceptación:**

- Una solicitud válida crea un procesamiento diferido para el audio recibido.
- El resultado conserva los datos de participantes aportados para asociarlos a las intervenciones cuando sea posible.
- Una solicitud sin archivo de audio válido informa de que no puede procesarse.

### RF-02 — Generar una transcripción diarizada de la sesión

- **Objetivo:** OBJ-1, OBJ-2
- **Ámbito:** Base
- **Estado:** Confirmado por Lay

El sistema debe generar, tras el procesamiento, una transcripción estructurada con intervenciones separadas por persona hablante y marcas temporales.

**Criterios de aceptación:**

- Para una grabación autorizada de clase individual o grupal, el resultado contiene el texto transcrito, las intervenciones diferenciadas y sus marcas temporales.
- Cuando se hayan aportado nombres, el resultado permite asociarlos a las personas hablantes identificadas.
- El procesamiento no exige resultados en tiempo real.

### RF-03 — Generar un análisis pedagógico y resumen general estructurados

- **Objetivo:** OBJ-1, OBJ-2
- **Ámbito:** Base
- **Estado:** Confirmado por Lay

El sistema debe extraer y clasificar, a partir de la transcripción, los contenidos relevantes para el aprendizaje de idiomas: vocabulario, gramática y construcciones, errores y correcciones, aciertos reforzados, explicaciones o conceptos clave y dudas resueltas. Debe incluir también un resumen general de la clase.

**Criterios de aceptación:**

- El resultado de una clase procesada contiene una sección de repaso separada de la transcripción.
- Cada elemento del repaso indica su categoría pedagógica.
- El resultado incluye un resumen general de la clase.
- Cuando el resultado use un fragmento concreto como evidencia, puede incluir su referencia temporal.

### RF-04 — Entregar resultados estructurados para consulta e integración

- **Objetivo:** OBJ-1, OBJ-2
- **Ámbito:** Base
- **Estado:** Confirmado por Lay

El sistema debe entregar un resultado estructurado que reúna la transcripción diarizada y el repaso pedagógico, de modo que CoTeach pueda integrarlo posteriormente mediante API.

**Criterios de aceptación:**

- El resultado incluye la transcripción completa y el repaso pedagógico de la misma sesión.
- Un consumidor de la API puede distinguir las dos partes sin interpretar texto libre.
- La demostración de diciembre permite consultar el resultado de al menos una sesión procesada.

### RF-05 — Revisar y publicar resultados al alumnado autorizado

- **Objetivo:** OBJ-2
- **Ámbito:** Base
- **Estado:** Alcance aprobado para el MVP; plazo provisional pendiente de validación por Lay

El sistema debe permitir que el profesorado revise y corrija los resultados antes de compartirlos con el alumnado autorizado. Si no hay revisión, debe publicarlos automáticamente al transcurrir el plazo configurado, propuesto provisionalmente en 24 horas.

**Criterios de aceptación:**

- El profesorado puede distinguir un resultado pendiente de revisión de uno revisado.
- Si el profesorado revisa y aprueba antes del plazo, las correcciones se reflejan en el resultado que se comparte.
- Si no hay revisión al vencer el plazo configurado, el resultado se publica automáticamente al alumnado autorizado.
- El plazo de revisión se configura sin fijarlo directamente en el código; para el MVP se propone 24 horas, pendiente de validación por Lay.

### RF-06 — Ofrecer resúmenes individualizados en clases grupales

- **Objetivo:** OBJ-2
- **Ámbito:** Evolución
- **Estado:** Segunda fase

El sistema debería ofrecer un repaso individualizado para cada alumno o alumna de una clase grupal.

**Criterios de aceptación:**

- Tras aprobar esta capacidad, una clase grupal puede producir resultados diferenciados por alumno o alumna.
- La asociación de cada resultado individual conserva la trazabilidad con las intervenciones correspondientes.

### RF-07 — Mostrar referencias temporales pedagógicas cuando aporten valor

- **Objetivo:** OBJ-2
- **Ámbito:** Evolución
- **Estado:** Segunda fase

El sistema debería incluir referencias temporales en elementos pedagógicos donde faciliten el repaso, como pronunciación o frases concretas.

**Criterios de aceptación:**

- Tras aprobar esta capacidad, los elementos seleccionados incluyen una referencia temporal navegable o consultable.
- La ausencia de referencia temporal en un elemento no impide entregar el resto del repaso.

## 10. Requisitos no funcionales

### RNF-01 — Privacidad por diseño y acceso limitado

- **Objetivo:** OBJ-3
- **Estado:** Confirmado por Lay

El producto debe procesar grabaciones consentidas o datos de prueba apropiados, evitar publicar información personal o sensible en el repositorio y limitar el acceso a profesorado y alumnado autorizados.

**Criterios de aceptación:**

- Los escenarios de demostración usan grabaciones autorizadas, simuladas o material externo utilizado de forma apropiada.
- No se versionan grabaciones ni datos personales o sensibles.
- La política concreta de consentimiento, autorización y acceso queda identificada como pendiente antes de producción.

### RNF-02 — Conservación limitada del audio original

- **Objetivo:** OBJ-3
- **Estado:** Confirmado por Lay

El audio original debe almacenarse en infraestructura propia y purgarse automáticamente transcurridos 14 días desde su recepción.

**Criterios de aceptación:**

- Una grabación procesada registra su momento de recepción y su fecha de purga a los 14 días.
- Transcurrido el plazo, el audio original deja de estar disponible para consulta o procesamiento.
- La duración de conservación de transcripciones y resultados se documenta antes de producción.

### RNF-03 — Software libre, interoperabilidad y soberanía tecnológica

- **Objetivo:** OBJ-4
- **Estado:** Confirmado por Lay

El producto debe priorizar software libre, estándares abiertos e infraestructura que preserve la soberanía tecnológica y evite dependencias innecesarias de proveedores.

**Criterios de aceptación:**

- Las decisiones técnicas posteriores documentan cómo cumplen este principio o qué excepción aprobada requieren.
- La interfaz de integración se describe mediante un formato abierto y versionable cuando se defina el contrato.

### RNF-04 — Eficiencia y primera capacidad operativa

- **Objetivo:** OBJ-4, OBJ-5
- **Estado:** Confirmado por Lay

El producto debe evaluar la eficiencia computacional junto con calidad, privacidad y coste, y estar orientado a una primera estimación de diez clases diarias con capacidad de evolución.

**Criterios de aceptación:**

- La demostración documenta el volumen de pruebas ejecutado y los recursos observados.
- Los límites de capacidad, coste y recursos necesarios se registran para decidir la evolución posterior.

### RNF-05 — Procesamiento no síncrono

- **Objetivo:** OBJ-1, OBJ-5
- **Estado:** Confirmado por Lay

El producto no requiere entregar la transcripción ni el repaso durante la clase; puede procesarlos después de que esta termine.

**Criterios de aceptación:**

- El flujo del MVP acepta que los resultados estén disponibles después de finalizar el procesamiento.
- No se define ningún compromiso de latencia en tiempo real.

## 11. Reglas de dominio

- **RD-01:** El audio original de una clase se conserva durante 14 días desde su recepción y se purga automáticamente al finalizar ese plazo.
- **RD-02:** Solo se procesan grabaciones consentidas o datos de prueba apropiados; no se publican datos personales o sensibles en el repositorio.
- **RD-03:** El MVP no cubre a menores de edad.
- **RD-04:** El servicio trata cada sesión de forma independiente; no requiere reconocer automáticamente a una misma persona entre sesiones.
- **RD-05:** La transcripción y el repaso son ayudas al aprendizaje y están sujetos al criterio y revisión del profesorado.
- **RD-06 (provisional, pendiente de validación por Lay):** Un resultado revisado y aprobado por el profesorado puede compartirse antes del vencimiento; si no se revisa, se publica automáticamente al alumnado autorizado al alcanzar el plazo configurable, propuesto en 24 horas para el MVP.

## 12. Restricciones, supuestos y riesgos

- **Restricciones confirmadas:** el MVP debe estar disponible para la presentación de diciembre; será un servicio independiente integrado por API; debe usar software libre, privacidad por diseño y priorizar soberanía tecnológica e impacto ecológico. CoTeach dispone de un servidor temporal con Odoo y usa servicios Nextcloud; la infraestructura y proveedor definitivos no están decididos.
- **Supuestos a validar:** se dispone de tres grabaciones reales y de grabaciones simuladas suficientes para evaluar el MVP; el servicio recibirá por API el audio comprimido y, cuando exista, los participantes; Odoo seguirá proporcionando la gestión administrativa y de usuarios.
- **Riesgos:**
  - **Diarización:** solapamientos de voz y clases grupales pueden impedir distinguir correctamente a las personas hablantes. Mitigación: evaluar con grabaciones individuales y grupales autorizadas, y explicitar las limitaciones en la demostración.
  - **Idiomas:** la cobertura y calidad para castellano, catalán, inglés, francés y chino no están confirmadas para el MVP. Mitigación: acordar los idiomas de la demostración y evaluarlos con muestras disponibles.
  - **Privacidad:** no existe aún una política específica de protección de datos. Mitigación: usar datos consentidos o simulados, limitar la conservación del audio y definir responsabilidades antes de producción.
  - **Recursos y coste:** solo hay GPU local y el presupuesto o posible uso de GPU remota privada no está definido. Mitigación: medir recursos con el flujo MVP y tomar una decisión de capacidad antes de escalar.
  - **Calendario:** el alcance completo puede exceder la presentación de diciembre. Mitigación: proteger el flujo Base RF-01 a RF-05 y posponer RF-06 y RF-07 a la segunda fase.
  - **Integración:** la documentación de CoTeach es un borrador no definitivo. Mitigación: mantener el servicio desacoplado y fijar el contrato de API cuando la documentación esté disponible.

## 13. Decisiones de producto

| ID | Decisión | Motivo | Estado |
|---|---|---|---|
| DEC-01 | El MVP será un servicio independiente, desacoplado de CoTeach e integrable mediante API. | CoTeach dispone de un prototipo y mockups no definitivos; Lay confirma este enfoque. | Aceptada |
| DEC-02 | El MVP procesará audio después de la clase, sin requisito de tiempo real. | Lay confirma que la transcripción en tiempo real no es necesaria. | Aceptada |
| DEC-03 | El audio original se conservará 14 días y se purgará automáticamente. | Lay fija dos semanas de conservación. | Aceptada |
| DEC-04 | Para diciembre, el flujo Base incluye RF-01 a RF-05; RF-06 y RF-07 se trasladan a una segunda fase. | Alcance aprobado para concentrar la demostración en el flujo completo de audio a resultados estructurados y publicación. | Aceptada |
| DEC-05 | Para el MVP se propone un plazo configurable de revisión de 24 horas; antes del plazo el profesorado puede aprobar la compartición y, al vencerlo sin revisión, el resultado se publica al alumnado autorizado. | Materializa el alcance aprobado de RF-05 sin fijar el plazo en el código. Requiere validación de Lay. | Propuesta |
| DEC-06 | La interfaz visual de demostración será un cliente web separado del servicio y consumirá su API versionada; la tecnología concreta pertenece a la arquitectura. | Lay acepta una presentación visual, pero esta no debe condicionar el contrato ni trasladar autorización o reglas de negocio fuera del servicio. | Propuesta |

## 14. Preguntas abiertas

- ¿Qué idiomas concretos deben estar soportados y demostrados en diciembre? Lay menciona castellano, catalán, inglés, francés y chino, pero permite reducir el alcance. **Bloquea:** criterios de aceptación de calidad lingüística y selección de datos de prueba.
- ¿Lay valida el plazo provisional configurable de 24 horas para la revisión docente y la publicación automática al alumnado autorizado? **Bloquea:** cerrar DEC-05 y la regla definitiva de RF-05.
- ¿Cuánto tiempo se conservarán transcripciones y resultados estructurados, y quién podrá eliminarlos antes de ese plazo? **Bloquea:** política completa de retención y acceso.
- ¿Cuál es el presupuesto disponible y bajo qué condiciones se podría usar infraestructura o GPU remota privada? **Bloquea:** límites de coste y evaluación de capacidad.
- ¿Qué consentimiento, información y responsabilidades de protección de datos se aplicarán a las grabaciones reales, especialmente antes de incorporar menores en una fase futura? **Bloquea:** paso a producción con datos reales.
- ¿Qué formato de resultado espera CoTeach y qué documentación estable de su API proporcionará? **Bloquea:** definición del contrato de integración.
