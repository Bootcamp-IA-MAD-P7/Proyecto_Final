## ADDED Requirements

### Requirement: Identidad visual consistente de la interfaz
La interfaz web SHALL aplicar una identidad visual consistente basada en los mockups aprobados de CoTeach-AI: texto e iconografía de alto contraste sobre superficies claras, acción principal azul/turquesa y estados semánticos distinguibles. La presentación SHALL usar elementos reutilizables para los controles y superficies equivalentes del flujo existente.

#### Scenario: Una pantalla del flujo existente se muestra
- **WHEN** una persona abre una pantalla ya implementada de la interfaz
- **THEN** los controles, tarjetas y mensajes equivalentes comparten los tokens visuales y los estados definidos por la experiencia de frontend.

#### Scenario: Se comunica un estado semántico
- **WHEN** la interfaz muestra éxito, aviso, error o información de procesamiento
- **THEN** el estado se distingue por texto e iconografía además de por color.

### Requirement: Presentación accesible y responsive
La interfaz web SHALL conservar una experiencia utilizable con teclado y lector de pantalla, contraste WCAG AA para texto y controles, y una disposición que se adapte a escritorio, tableta y móvil (RNF-01).

#### Scenario: Una persona navega solo con teclado
- **WHEN** recorre los controles interactivos de una pantalla
- **THEN** el foco es visible, el orden de tabulación es lógico y cada control tiene un nombre accesible.

#### Scenario: La interfaz se ve en una pantalla estrecha
- **WHEN** el ancho disponible no permite dos columnas legibles
- **THEN** los paneles se reorganizan en una columna sin ocultar acciones ni información disponibles.

### Requirement: Navegación visual acorde con el rol sin autorización cliente
La interfaz SHALL poder mostrar navegación configurada para profesorado y alumnado solo hacia rutas que estén implementadas y disponibles para la sesión. La interfaz SHALL dejar la decisión de acceso y permisos a la API (RNF-01).

#### Scenario: Una ruta futura no está implementada
- **WHEN** el modelo visual del rol incluye una sección que aún no tiene una ruta funcional
- **THEN** la interfaz no la presenta como un enlace o acción disponible.

#### Scenario: La API rechaza una acción
- **WHEN** una persona intenta una acción que el servidor no autoriza
- **THEN** la interfaz muestra el error recibido y no interpreta la navegación visual como concesión de permiso.

### Requirement: Sin contenido simulado para capacidades no implementadas
La interfaz SHALL no presentar datos sintéticos, contadores, calendarios, recursos o acciones que hagan parecer disponible una capacidad fuera del MVP o aún no implementada.

#### Scenario: Un mockup ilustra una capacidad futura
- **WHEN** una sección de un mockup no corresponde a una ruta y datos reales o sintéticos ya soportados por el flujo del MVP
- **THEN** se limita a orientar el diseño y no se incorpora como contenido funcional o decorativo en la interfaz.
