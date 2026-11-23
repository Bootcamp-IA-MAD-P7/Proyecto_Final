# Spec Delta

## Purpose

Definir los invariantes observables de intercambio del MVP para que API, inferencia e interfaz puedan integrarse mediante contratos compartidos y pruebas sintéticas.

El delta completo es una propuesta pendiente de aprobación. Los campos se definen en [design.md](../../design.md); su futura fuente normativa será el contrato registrado según [CONTRACTS](../../../../../docs/CONTRACTS/README.md). No se declaran aprobadas las opciones técnicas de los ADR.

## ADDED Requirements

### Requirement: Identidad estable de recursos
El servicio SHALL conservar identificadores opacos de clase, trabajo y versión de resultado en sus intercambios, sin usar nombres de personas como claves (RF-01, RF-04, RNF-01).

#### Scenario: Consultas repetidas
- **WHEN** un consumidor autorizado consulta dos veces el mismo trabajo sin cambios
- **THEN** recibe los mismos identificadores y versión, sin crear otra clase.

#### Scenario: Asociación ajena
- **WHEN** una corrección referencia un participante de otra clase
- **THEN** se rechaza sin alterar la asociación existente.

### Requirement: Recepción interoperable e idempotente
El servicio SHALL aceptar audio comprimido y metadatos según el contrato, devolver identificación del trabajo diferido y distinguir cargas inválidas y conflictos de idempotencia (RF-01, RNF-05).

#### Scenario: Carga válida
- **WHEN** el emisor autorizado entrega una carga válida
- **THEN** recibe 202 y referencias consultables de clase y trabajo, sin esperar a la inferencia.

#### Scenario: Reenvío idéntico
- **WHEN** el mismo emisor repite clave de idempotencia y contenido
- **THEN** obtiene las referencias originales sin duplicar el trabajo.

#### Scenario: Clave reutilizada
- **WHEN** el emisor repite una clave con otro contenido
- **THEN** recibe conflicto 409 sin sustituir la carga original.

#### Scenario: Entrada inválida
- **WHEN** falta audio, hay identificadores de participantes duplicados o su número no concuerda
- **THEN** recibe error de validación y no se acepta un trabajo.

#### Scenario: Referencia de consentimiento ausente o inválida
- **WHEN** la carga no incluye consent_reference o su referencia no es válida según el contrato
- **THEN** recibe 422 invalid_consent_reference y no se acepta un trabajo ni se inicia inferencia.

Recibir una referencia y validar su estructura no verifica que exista consentimiento. El mecanismo y la responsabilidad de comprobar el consentimiento al que remite siguen pendientes de acordar; este escenario no los da por resueltos.

#### Scenario: Límites de entrada
- **WHEN** una carga supera el límite configurado o usa un formato no admitido
- **THEN** recibe respectivamente 413 o 415 sin inferencia; los límites concretos se acordarán antes de aceptar el contrato.

### Requirement: Estados y errores distinguibles
El servicio SHALL exponer estado y etapa del trabajo, distinguir espera, fallo y resultado disponible, y comunicar errores con código estable y posibilidad de reintento sin datos sensibles (RF-01, RF-04, RNF-01).

#### Scenario: Fallo de procesamiento
- **WHEN** una etapa falla
- **THEN** el trabajo informa fallo o espera de reintento y no representa un resultado como publicable.

#### Scenario: Audio vencido
- **WHEN** se necesita reprocesar un audio ya purgado según RNF-02
- **THEN** se informa que la fuente no está disponible y no se inicia inferencia con una copia retenida.

### Requirement: Resultado estructurado coherente
El servicio SHALL representar transcripción y análisis por separado, con marcas temporales de transcripción, hablantes de sesión y resumen general, validando referencias y categorías del RF-03 (RF-02, RF-03, RF-04, RD-04).

#### Scenario: Resultado válido
- **WHEN** el consumidor recibe un resultado completo
- **THEN** puede distinguir segmentos, hablantes, resumen general e ítems pedagógicos sin analizar texto libre para identificar su estructura.

#### Scenario: Hablante sin nombre
- **WHEN** no existe asociación fiable entre voz y participante
- **THEN** el resultado conserva un hablante de sesión sin asignación, sin deducir identidad por el orden de nombres.

#### Scenario: Resultado malformado
- **WHEN** un productor entrega intervalos negativos o invertidos, hablantes inexistentes o categorías desconocidas
- **THEN** se rechaza el resultado como completo y no se publica.

#### Scenario: Categoría vacía
- **WHEN** no se detectan elementos de una categoría
- **THEN** la representación admite ausencia de ítems de esa categoría sin fabricar contenido.

La validación estructural del resultado no garantiza su calidad pedagógica. Esta se evaluará con requisitos y escenarios de las specs funcionales posteriores, en particular pedagogical-analysis.

### Requirement: Autorización por clase y publicación
El servicio SHALL verificar identidad y autorización por clase en carga, consulta y revisión; el alumnado solo recibe versiones publicadas y el profesorado asignado puede acceder al borrador (RF-04, RF-05, RNF-01).

#### Scenario: Identidad inválida
- **WHEN** la credencial falta, caducó o es inválida
- **THEN** se rechaza la solicitud con 401 sin datos de la clase.

#### Scenario: Acceso transversal
- **WHEN** una persona autenticada intenta consultar un trabajo o resultado de otra clase
- **THEN** se deniega sin contenido ni metadatos de ese recurso.

#### Scenario: Borrador solicitado por alumno
- **WHEN** un alumno autorizado consulta una clase todavía no publicada
- **THEN** no recibe transcripción ni análisis en borrador.

#### Scenario: Rol falsificado
- **WHEN** un alumno declara rol docente en el cuerpo de una corrección
- **THEN** no obtiene permisos de revisión.

### Requirement: Revisión versionada y publicación consistente
El servicio SHALL identificar la versión revisada y publicada, rechazar actualizaciones obsoletas y representar aprobación o publicación automática según RF-05 y RD-06 provisional. El plazo se comunica como dato configurado, no como constante del contrato.

#### Scenario: Corrección obsoleta
- **WHEN** un docente intenta guardar o aprobar una versión que ya cambió
- **THEN** recibe conflicto 409 y no sobrescribe la versión vigente.

#### Scenario: Aprobación anticipada
- **WHEN** el docente autorizado aprueba la versión vigente antes del vencimiento
- **THEN** esa versión queda efectivamente publicada y disponible para consulta del alumnado autorizado.

#### Scenario: Vencimiento sin revisión
- **WHEN** vence el plazo configurado de un resultado válido sin revisión
- **THEN** la versión publicada se identifica como automática; 24 horas es un valor provisional sujeto a Lay.

#### Scenario: Carrera de publicación
- **WHEN** aprobación y vencimiento concurren sobre la misma versión
- **THEN** el consumidor observa una sola publicación consistente, sin duplicados ni sustitución por una versión obsoleta.

Pendiente de confirmación por Lay: qué ocurre si vence el plazo mientras la revisión está iniciada pero no aprobada. Los escenarios anteriores no establecen si en ese caso se publica, se bloquea o se amplía el plazo; esa regla debe resolverse antes de implementar el caso.

### Requirement: Compatibilidad explícita
El contrato SHALL distinguir versión del esquema de versión del resultado, documentar ampliaciones compatibles y tratar cambios incompatibles como nueva versión mayor con migración (RF-04, RNF-03).

#### Scenario: Campo opcional añadido
- **WHEN** se añade un campo opcional compatible
- **THEN** consumidores existentes pueden seguir interpretando sus campos conocidos.

#### Scenario: Cambio incompatible
- **WHEN** se elimina un campo obligatorio o cambia su significado
- **THEN** se declara nueva versión mayor y migración, sin presentarlo como ampliación compatible.
