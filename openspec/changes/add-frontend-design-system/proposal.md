# Proposal

## Why

La interfaz de demostración ya permite recorrer el flujo del MVP, pero su presentación provisional no representa la identidad visual aprobada para CoTeach-AI. Los mockups aportan un lenguaje común para profesorado y alumnado que debe convertirse en una base reutilizable, accesible y responsive, sin alterar las reglas de negocio ni el contrato.

La Issue #66 es transversal al MVP y su adscripción definitiva a una épica sigue pendiente de confirmación del equipo. Esta propuesta la vincula a la Issue #66 sin asignarle una épica de forma artificial.

## What Changes

- Crear la capacidad de experiencia de frontend: identidad visual coherente, componentes de presentación accesibles y estructura preparada para navegación visual por rol.
- Catalogar los cuatro mockups aprobados por pantalla y rol, sin transformar sus datos de ejemplo en datos de producto.
- Sustituir la paleta provisional del frontend por los tokens derivados de los mockups: azul marino, azul y turquesa, superficies cálidas y estados semánticos.
- Establecer estilos base responsive y componentes visuales mínimos reutilizables, sin conectar todavía las nuevas piezas a `App.tsx`, subida, seguimiento, mocks ni pruebas de la Issue #48.
- Planificar la integración posterior de las pantallas existentes después de que la Issue #48 se integre en `dev`.

## Capabilities

### New Capabilities

- `frontend-experience`: La interfaz web presenta de forma consistente, accesible y responsive las capacidades ya disponibles, y ofrece navegación visual acorde con el rol sin tomar decisiones de autorización.

### Modified Capabilities

- Ninguna.

## Impact

- Afecta al cliente React/TypeScript/Vite, sus estilos y sus pruebas unitarias de componentes.
- Afecta a `docs/design/` al catalogar los mockups aprobados y al documentar el sistema de diseño.
- No cambia backend, OpenAPI, contratos en `docs/CONTRACTS/`, autenticación, reglas de autorización ni dependencias.
- Se apoya en RF-01, RF-04 y RF-05 como flujos que la interfaz representa, y en RNF-01 para no sustituir la autorización del servidor; no modifica sus requisitos.
