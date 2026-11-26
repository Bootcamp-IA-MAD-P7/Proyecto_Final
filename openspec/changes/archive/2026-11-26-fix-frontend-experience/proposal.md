# Proposal

## Why

La validación manual ha confirmado que la apariencia de la web conserva rasgos del walking skeleton y que el alumnado recibe un formulario docente de subida, aunque la API lo rechaza correctamente. Esta corrección alinea la experiencia visible con los mockups aprobados y evita presentar una acción que no corresponde al rol, sin sustituir la autorización del servidor.

La Issue #66 sigue siendo transversal al MVP y no tiene una adscripción definitiva a una épica. Este cambio de corrección se vincula a #66 sin modificar el cambio previamente archivado.

## What Changes

- Corregir la composición visual de las pantallas existentes: jerarquía tipográfica, marca, iconografía, shell, tarjetas, controles, selector de archivos, progreso y botones según los cuatro mockups aprobados.
- Localizar al castellano la presentación de etapas de procesamiento y categorías pedagógicas, conservando los valores del contrato API.
- Impedir que el alumnado vea o alcance el formulario docente de subida, tanto tras iniciar sesión como mediante `/upload` o la marca de cabecera.
- Mantener disponible para alumnado autorizado el acceso directo a resultados publicados; no se crea una lista, calendario ni datos sintéticos mientras no exista esa capacidad.
- Ocultar la aprobación cuando la publicación real del resultado ya esté completada, sin realizar solicitudes redundantes.
- Compactar los espacios verticales de las vistas existentes y adaptar el selector de audio a pantallas estrechas sin alterar su accesibilidad.
- Mantener contraste WCAG AA, teclado, lector de pantalla, funcionalidades y regresiones existentes.
- Aislar las consultas y la caché de frontend por identidad de sesión, para que ningún cierre de sesión emita peticiones sin credencial ni exponga datos o errores de una sesión anterior.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `frontend-experience`: La presentación visual y la navegación por rol se corrigen para no exponer la subida docente a alumnado y para representar estados API en lenguaje visible coherente.

## Impact

- Afecta al cliente React/TypeScript/Vite, sus estilos, componentes visuales y pruebas.
- Afecta a los requisitos visuales y de navegación de `frontend-experience`; se apoya en RF-01, RF-04, RF-05 y RNF-01, sin cambiar contratos, backend ni OpenAPI.
- No añade dependencias, rutas de producto, datos ficticios, funciones de calendario, biblioteca, recursos ni autorización de cliente.
