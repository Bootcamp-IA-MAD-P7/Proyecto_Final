# Spec Delta

## ADDED Requirements

### Requirement: Repaso pedagógico estructurado visible
La interfaz SHALL presentar, junto a la transcripción ya disponible, el resumen general y los elementos de análisis recibidos de la API, agrupados visualmente en las seis categorías del contrato y sin transformar los valores ni el contenido recibidos (RF-03, RF-04, RNF-01).

#### Scenario: Resultado con resumen y varias categorías
- **WHEN** la API devuelve un análisis con resumen y elementos de varias categorías
- **THEN** la interfaz muestra primero el resumen general y agrupa los elementos por su categoría pedagógica localizada.

#### Scenario: Categoría sin elementos
- **WHEN** la API devuelve un análisis sin elementos para una de las seis categorías
- **THEN** la interfaz comunica que esa categoría no contiene hallazgos sin inventar elementos ni ocultar las demás categorías.

### Requirement: Diseño accesible del repaso pedagógico
La presentación del repaso SHALL reutilizar el sistema de diseño de CoTeach-AI, conservar contraste WCAG AA, nombres accesibles y navegación por teclado, y reorganizar resumen y categorías para escritorio, tableta y móvil sin perder información (RF-03, RF-04, RNF-01).

#### Scenario: Pantalla estrecha
- **WHEN** la vista de resultado se muestra en una tableta o móvil
- **THEN** el resumen y las categorías se disponen en una sola columna legible, sin desplazamiento horizontal ni acciones inaccesibles.

#### Scenario: Navegación por teclado
- **WHEN** una persona recorre la vista de análisis con teclado o lector de pantalla
- **THEN** puede identificar el resumen, cada encabezado de categoría y sus contenidos en un orden lógico.

### Requirement: Estado de análisis vacío claro
La interfaz SHALL diferenciar un análisis válido sin contenidos pedagógicos de un resultado que todavía no está disponible o que la API rechaza, conservando el tratamiento existente de errores y autorización (RF-03, RF-04, RNF-01).

#### Scenario: Análisis válido sin hallazgos
- **WHEN** la API devuelve un resumen y una lista vacía de elementos de análisis
- **THEN** la interfaz muestra un estado vacío claro y no presenta datos simulados.

#### Scenario: Resultado no disponible o no autorizado
- **WHEN** la consulta de resultado falla conforme al contrato
- **THEN** la interfaz conserva el mensaje de estado o error aplicable y no lo sustituye por un estado vacío de análisis.
