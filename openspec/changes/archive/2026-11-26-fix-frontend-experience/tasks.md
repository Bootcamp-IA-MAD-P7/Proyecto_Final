# Tasks

Corrección posterior a la validación manual de la Issue #66. No modifica el cambio archivado `add-frontend-design-system` y mantiene este cambio activo hasta una aprobación manual visual posterior.

## 1. Corrección de experiencia visual y acceso de alumnado (frontend) · #66

**Criterios de aceptación:**
- La interfaz de profesor y alumno refleja los cuatro mockups como referencia principal: marca, iconografía, jerarquía tipográfica contenida, shell integrado, tarjetas, márgenes, controles y acciones coherentes.
- El alumnado no ve ni puede alcanzar el formulario de subida tras iniciar sesión, por acceso directo a `/upload` ni mediante la marca; no se crean datos ni capacidades de alumnado inexistentes.
- Una persona alumna conserva el acceso directo a un resultado publicado que la API autoriza y no ve controles docentes de aprobación.
- La API sigue siendo la autoridad: el cliente conserva el tratamiento de 403 y las pruebas de regresión de #48.
- Las etapas y categorías conocidas se presentan en castellano; el valor del contrato API no se modifica y, sin porcentaje real de API, el progreso es indeterminado.
- Escritorio, tableta y móvil mantienen acciones disponibles y navegación de teclado, con contraste WCAG AA y controles accesibles.
- `npm run lint`, `npm run test`, `npm run build` y `openspec validate fix-frontend-experience --strict` pasan.

**Depende de:** —

- [x] 1.1 Implementar mapeos puros de presentación para etapas y categorías del contrato, con pruebas de etiquetas en castellano y de indicador indeterminado cuando no existe porcentaje API.
- [x] 1.2 Corregir el destino inicial, el acceso directo a subida y la marca según rol; añadir pruebas de que alumnado no recibe el formulario, conserva resultados publicados autorizados y se mantiene la regresión 403.
- [x] 1.3 Ajustar el sistema visual y los componentes de las pantallas existentes —marca SVG, iconos mínimos, tipografía, shell, tarjetas, botones, selector accesible y progreso— con pruebas de accesibilidad, contraste y comportamiento responsive.
- [x] 1.4 Ejecutar las regresiones del frontend (`npm run lint`, `npm run test`, `npm run build`) y validar el cambio con `openspec validate fix-frontend-experience --strict`.
- [x] 1.5 Aplicar los ajustes finales de validación manual: compactar acceso y móvil, eliminar duplicidades de texto, ocultar aprobación publicada según el estado API y adaptar el selector de audio; ampliar regresiones y repetir validaciones.
- [x] 1.6 Aislar las consultas protegidas por identidad de sesión: impedir peticiones sin token, cancelar y vaciar caché al salir y añadir regresiones de cierre, cambio de perfil y consulta autorizada de alumnado.
- [x] 1.7 Corregir el indicador `:focus-visible` de la marca CoTeach-AI para limitarlo al logotipo con anillo azul redondeado y conservar la navegación por teclado.

## Workflow follow-up

- Realizar revisión independiente tras el apply y corregir sus hallazgos dentro del alcance.
- Esperar la validación manual visual y funcional de la persona antes de sincronizar specs o archivar `fix-frontend-experience`.
