## MODIFIED Requirements

### Requirement: Identidad visual consistente de la interfaz
La interfaz web SHALL aplicar una identidad visual fiel a los mockups aprobados de CoTeach-AI: marca gráfica, iconografía coherente, jerarquía tipográfica contenida, texto e iconografía de alto contraste sobre superficies claras, acción principal azul/turquesa y estados semánticos distinguibles. La presentación SHALL usar elementos reutilizables para los controles y superficies equivalentes del flujo existente.

#### Scenario: Una pantalla del flujo existente se muestra
- **WHEN** una persona abre una pantalla ya implementada de la interfaz
- **THEN** los controles, tarjetas, marca, mensajes y acciones equivalentes comparten los tokens visuales y los estados definidos por la experiencia de frontend.

#### Scenario: Selector de audio en pantalla estrecha
- **WHEN** el ancho móvil no permite una línea legible para el nombre de grabación y la acción de exploración
- **THEN** el selector reorganiza sus elementos sin comprimir innecesariamente el texto y conserva su etiqueta y foco accesibles.

#### Scenario: Se comunica un estado semántico
- **WHEN** la interfaz muestra éxito, aviso, error o información de procesamiento
- **THEN** el estado se distingue por texto e iconografía además de por color.

#### Scenario: La marca recibe foco de teclado
- **WHEN** una persona alcanza el logotipo CoTeach-AI con teclado
- **THEN** la marca muestra un anillo azul redondeado limitado a su propio contenido, visible tanto en la vista pública como autenticada.

### Requirement: Presentación accesible y responsive
La interfaz web SHALL conservar una experiencia utilizable con teclado y lector de pantalla, contraste WCAG AA para texto y controles, y una disposición que se adapte a escritorio, tableta y móvil (RNF-01).

#### Scenario: Una persona navega solo con teclado
- **WHEN** recorre los controles interactivos de una pantalla
- **THEN** el foco es visible, el orden de tabulación es lógico y cada control tiene un nombre accesible.

#### Scenario: La interfaz se ve en una pantalla estrecha
- **WHEN** el ancho disponible no permite dos columnas legibles
- **THEN** los paneles se reorganizan en una columna sin ocultar acciones ni información disponibles.

#### Scenario: Vista de escritorio
- **WHEN** la interfaz se muestra con espacio de escritorio
- **THEN** la cabecera, navegación lateral y contenido mantienen una jerarquía visual integrada sin ocultar acciones disponibles ni provocar desplazamiento horizontal.

#### Scenario: Vista de tableta
- **WHEN** la interfaz se muestra con ancho de tableta
- **THEN** el shell conserva acceso a las acciones disponibles y ajusta sus columnas sin solapamientos.

#### Scenario: Vista móvil
- **WHEN** la interfaz se muestra con ancho móvil
- **THEN** los paneles y la navegación se reorganizan en una columna sin ocultar acciones ni información disponibles.

### Requirement: Navegación visual acorde con el rol sin autorización cliente
La interfaz SHALL poder mostrar navegación configurada para profesorado y alumnado solo hacia rutas que estén implementadas y disponibles para la sesión. La interfaz SHALL dejar la decisión de acceso y permisos a la API (RNF-01).

#### Scenario: Una ruta futura no está implementada
- **WHEN** el modelo visual del rol incluye una sección que aún no tiene una ruta funcional
- **THEN** la interfaz no la presenta como un enlace o acción disponible.

#### Scenario: Alumno ante la subida docente
- **WHEN** una persona autenticada con rol de alumnado inicia sesión, abre directamente `/upload` o activa la marca de cabecera
- **THEN** la interfaz no muestra el formulario de subida y la dirige a su vista disponible sin concederle permisos de cliente.

#### Scenario: Alumno ante un resultado publicado autorizado
- **WHEN** una persona autenticada con rol de alumnado abre un resultado que la API autoriza por estar publicado
- **THEN** la interfaz conserva el acceso al resultado y no muestra controles docentes de aprobación.

#### Scenario: La API rechaza una acción
- **WHEN** una persona intenta una acción que el servidor no autoriza
- **THEN** la interfaz muestra el error recibido y no interpreta la navegación visual como concesión de permiso.

#### Scenario: Resultado ya publicado
- **WHEN** la API devuelve un resultado con `publication.status` igual a `published`
- **THEN** la interfaz confirma que está publicado y no muestra ni envía una aprobación redundante.

#### Scenario: Cierre y cambio de sesión
- **WHEN** una persona cierra sesión desde una pantalla que consulta datos protegidos y otra persona inicia una sesión
- **THEN** la interfaz cancela y elimina las consultas de la sesión anterior, no emite solicitudes sin credencial y separa la caché por identidad sin usar el token como clave.

#### Scenario: Inicio de alumnado sin resultado abierto
- **WHEN** una persona de alumnado inicia sesión en su vista inicial
- **THEN** la interfaz no consulta resultados hasta que la persona abre una ruta de resultado autorizada.

## ADDED Requirements

### Requirement: Presentación localizada de valores de procesamiento
La interfaz SHALL presentar en castellano las etapas y categorías recibidas del contrato API, sin transformar los valores enviados o recibidos por dicho contrato (RF-01, RF-04).

#### Scenario: Etapa de procesamiento visible
- **WHEN** la API devuelve una etapa de trabajo conocida
- **THEN** la interfaz muestra su etiqueta localizada y usa un indicador indeterminado mientras el contrato no aporte un porcentaje real.

#### Scenario: Categoría pedagógica visible
- **WHEN** el resultado contiene una categoría pedagógica del contrato
- **THEN** la interfaz muestra una etiqueta localizada sin modificar el valor original ni el contenido pedagógico.
