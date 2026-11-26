# Spec Delta

## Purpose

Que una transcripción diarizada procesada produzca un repaso pedagógico estructurado, útil y evaluable, sin alterar su separación contractual respecto de la transcripción.

## ADDED Requirements

### Requirement: Repaso pedagógico estructurado desde la transcripción
Cuando una clase tenga una transcripción procesada, el servicio SHALL generar y conservar un análisis conforme al contrato [API de CoTeach AI](../../../../../docs/CONTRACTS/coteach-ai-api.md), separado de la transcripción y compuesto por un resumen general y elementos pedagógicos válidos (RF-03, RF-04).

#### Scenario: Clase con contenidos pedagógicos identificados
- **WHEN** finaliza el análisis de una transcripción de clase con contenidos relevantes
- **THEN** el resultado consultable contiene `general_summary` y elementos de análisis separados de sus segmentos de transcripción.

#### Scenario: Análisis sin elementos identificables
- **WHEN** finaliza el análisis de una transcripción sin contenidos que clasificar
- **THEN** el resultado contiene un resumen que refleje la sesión y una lista de elementos vacía, sin inventar contenido.

### Requirement: Categorías pedagógicas completas y contractuales
El análisis SHALL clasificar cada elemento únicamente como `vocabulary`, `grammar`, `errors_corrections`, `reinforced_successes`, `key_concepts` o `resolved_questions`; cada una corresponde, respectivamente, a vocabulario, gramática y construcciones, errores y correcciones, aciertos reforzados, explicaciones o conceptos clave y dudas resueltas (RF-03, RF-04).

#### Scenario: Elementos de varias categorías
- **WHEN** la transcripción contiene contenidos de varias categorías pedagógicas
- **THEN** cada elemento devuelto conserva una de las seis categorías contractuales y contenido no vacío.

#### Scenario: Categoría sin hallazgos
- **WHEN** no se identifica contenido para una de las seis categorías
- **THEN** el resultado no crea un elemento artificial para esa categoría y sigue siendo válido.

### Requirement: Cobertura de transcripciones largas sin duplicados
Cuando la transcripción exceda el contexto utilizable del generador, el servicio SHALL analizarla por fragmentos y consolidar sus resultados de modo que el análisis cubra todos los fragmentos y no duplique elementos pedagógicos equivalentes (RF-03, RF-04, RNF-04).

#### Scenario: Transcripción que supera el contexto del modelo
- **WHEN** una transcripción requiere más de un fragmento para su análisis
- **THEN** el resultado consolidado conserva la cobertura de todos los fragmentos y un resumen general de la sesión.

#### Scenario: Hallazgo repetido en varios fragmentos
- **WHEN** dos fragmentos producen elementos pedagógicos equivalentes
- **THEN** el resultado consolidado no los devuelve duplicados.

### Requirement: Transcripción tratada como datos no confiables
El servicio SHALL tratar el texto de la transcripción exclusivamente como datos a analizar; las instrucciones incrustadas en él no SHALL cambiar permisos, configuración, herramientas ni acciones del sistema (RF-03, RNF-01).

#### Scenario: Instrucción maliciosa en una transcripción
- **WHEN** una transcripción contiene texto que intenta modificar el procesamiento o pedir una acción externa
- **THEN** el servicio lo analiza como contenido de clase y conserva sus permisos, configuración y flujo de procesamiento.

### Requirement: Fallo seguro del análisis
El servicio SHALL tratar como fallo del procesamiento una generación o validación de análisis que no pueda producir un resultado conforme al contrato; no SHALL dejar un resultado nuevo consultable o publicable de ese intento (RF-03, RF-04, RNF-01).

#### Scenario: Salida no válida del generador
- **WHEN** la salida generada no puede validarse como análisis del contrato
- **THEN** el trabajo termina según la política de errores del procesamiento sin persistir un resultado de análisis parcial.

#### Scenario: Modelo de análisis no disponible
- **WHEN** la etapa de análisis no puede ejecutarse porque su modelo o dependencia no está disponible
- **THEN** el trabajo informa un error de procesamiento conforme al contrato y no sustituye silenciosamente el modelo ni crea un análisis sintético.

### Requirement: Evaluación separada de calidad pedagógica y recursos
Antes de declarar apto un modelo de análisis para la demostración, el equipo SHALL registrar una evaluación reproducible con transcripciones sintéticas o autorizadas, una rúbrica de revisión humana y medidas de recursos, sin incorporar transcripciones de clase ni datos personales al repositorio (RF-03, RNF-01, RNF-04).

#### Scenario: Evaluación preliminar de candidatos
- **WHEN** se compara un candidato de modelo antes de integrarlo en el worker
- **THEN** se conservan la versión del candidato, las entradas sintéticas o autorizadas permitidas, el resultado de la rúbrica y las métricas de tiempo y memoria sin publicar contenido de clases.

#### Scenario: Validación técnica sin evaluación pedagógica
- **WHEN** un candidato solo supera la validación estructural o las pruebas automatizadas
- **THEN** no se considera demostrada su calidad pedagógica para la presentación.
