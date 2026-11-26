# Sistema de diseño del frontend

## Principios

La interfaz toma de los mockups una composición clara y calmada: fondo cálido, texto azul marino, superficies blancas, acción azul/turquesa y estados suaves pero distinguibles. Profesorado y alumnado comparten esos fundamentos; solo cambiarán navegación y contenido cuando existan rutas funcionales. La navegación nunca concede permisos: los decide la API.

## Tokens

Los tokens viven en `frontend/src/styles/tokens.css`. La escala de espacio usa 4 px como unidad; los tamaños habituales son 8, 12, 16, 24, 32 y 48 px. Los controles usan radio de 12 px y las tarjetas, 20–24 px. Las sombras son amplias y de baja opacidad.

| Grupo | Valores |
| --- | --- |
| Texto y superficie | tinta `#081D45`, fondo `#FCF9F6`, tarjeta `#FFFFFF`, borde `#D7E0EB` |
| Acción | azul `#0876B9`, azul intenso `#006AA4`, turquesa `#007A83` |
| Superficies suaves | información `#E7F5FF`, turquesa `#E7FAF7` |
| Estados | éxito `#187A3E`, aviso `#9B5600`, error `#B82F28` |

Los gradientes se limitan a acciones principales y zonas destacadas: `#006AA4` a `#007A83`. Ambos extremos permiten texto blanco con contraste AA. Los estados siempre combinan color, texto e icono.

## Tipografía

La aplicación no distribuye Inter, no la carga desde una hoja externa y el entorno de desarrollo comprobado no la tiene instalada. Por tanto, `Inter` es una preferencia no garantizada y la pila efectiva es `Inter, ui-sans-serif, system-ui, sans-serif`; el sistema operativo provee el fallback. No se añade una descarga de fuentes ni una dependencia nueva.

Los títulos usan peso 700–800 y espaciado ligeramente compacto; cuerpo y metadatos priorizan legibilidad. Los tamaños deben usar los tokens tipográficos y no valores arbitrarios.

## Accesibilidad y responsive

- Texto, iconos y controles interactivos tienen contraste WCAG AA; `frontend/src/styles/contrast.test.ts` verifica los pares de tokens y los extremos del gradiente.
- El foco usa un anillo de 3 px, con un color visible sobre las superficies claras.
- Los avisos exponen un rol accesible y las insignias incluyen texto explícito.
- Los componentes no fijan anchos: el futuro layout pasa de varias columnas a una sola cuando el espacio deja de ser legible.
- Se respeta `prefers-reduced-motion` para las transiciones de progreso.
