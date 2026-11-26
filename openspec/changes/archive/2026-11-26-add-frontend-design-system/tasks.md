# Tasks

Plan de la funcionalidad `add-frontend-design-system` para la Issue #66, transversal al MVP y pendiente de adscripción definitiva a una épica. La primera historia deja los cimientos visuales aislados; las siguientes no se inician hasta resolver sus dependencias funcionales.

## 1. Cimientos visuales aislados (frontend) · #66

**Criterios de aceptación:**
- Los cuatro mockups aprobados permanecen en `docs/design/mockups/` con su nombre original y están catalogados por pantalla y rol.
- El sistema de diseño documenta sus tokens, jerarquía, geometría, estados, responsive, accesibilidad y el uso limitado de degradados.
- El frontend dispone de tokens CSS, estilos base y componentes presentacionales reutilizables sin modificar `App.tsx`, `styles.css`, subida, seguimiento, mocks ni pruebas afectados por #48.
- Se comprueba la disponibilidad de Inter y cada combinación visual usada cumple contraste WCAG AA; los estados no dependen solo del color.
- Las pruebas unitarias cubren las variantes y la accesibilidad básica de los componentes; lint, test, build y la validación OpenSpec pasan.

**Depende de:** —

- [x] 1.1 Catalogar los cuatro mockups en `docs/design/` conservando nombre, pantalla y rol, y documentar el sistema visual aprobado sin incorporar datos de ejemplo como producto.
- [x] 1.2 Comprobar y documentar la disponibilidad efectiva de Inter y la pila de fallback sin añadir dependencias.
- [x] 1.3 Crear tokens CSS y estilos base aislados; verificar programáticamente contraste AA de colores, extremos de degradados, foco y estados.
- [x] 1.4 Implementar los componentes presentacionales mínimos (`Button`, `Card`, `StatusBadge`, `InlineNotice` y `ProgressIndicator`) sin conectarlos a pantallas existentes.
- [x] 1.5 Añadir pruebas unitarias de variantes, texto/roles accesibles y estados semánticos; ejecutar lint, test y build del frontend.

## 2. Composición visual de las rutas existentes (frontend)

**Criterios de aceptación:**
- Tras integrarse #48 en `dev`, las pantallas ya existentes usan los cimientos de la historia 1 sin cambiar el comportamiento de subida, seguimiento, resultado ni revisión.
- La composición no añade rutas, datos o acciones fuera del MVP.
- Las regresiones de #48 y del flujo existente siguen pasando.

**Depende de:** 1 y la integración de la Issue #48 en `dev`

- [x] 2.1 Reconciliar los estados y pruebas que aporte #48 con los componentes visuales.
- [x] 2.2 Adaptar las rutas existentes al shell y a los componentes reutilizables, conservando su comportamiento y mensajes.
- [x] 2.3 Añadir regresiones visuales y de accesibilidad proporcionadas al comportamiento ya disponible.

## 3. Navegación visual por rol e integración (frontend)

**Criterios de aceptación:**
- La navegación distingue la composición docente y alumna solo para rutas funcionales y no concede permisos de cliente.
- Los diseños de escritorio, tableta y móvil conservan las acciones disponibles y el uso por teclado.
- El cambio completo valida contra la especificación y no deja tareas de la funcionalidad pendientes.

**Depende de:** 1, 2 y las rutas funcionales que correspondan al flujo MVP

- [x] 3.1 Incorporar el shell y la navegación configurada por rol para rutas implementadas, sin representar capacidades futuras como disponibles.
- [x] 3.2 Verificar responsive y accesibilidad del flujo disponible en los tres rangos de pantalla.
- [x] 3.3 Ejecutar `verify` completo, sincronizar las specs y archivar el cambio desde el PR de integración.
