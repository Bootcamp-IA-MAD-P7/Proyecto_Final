## Contexto

La Issue #66 traslada a la interfaz React existente la identidad de cuatro mockups aprobados. El frontend actual contiene un flujo de demostración (inicio de sesión sintético, subida, seguimiento, resultado y revisión) y la Issue #48 está ampliando subida y estados. Esta funcionalidad no cambia la API, la lógica de negocio ni la autoridad del backend.

Los mockups se catalogarán con sus nombres originales:

| Archivo | Pantalla de referencia | Rol |
| --- | --- | --- |
| `Panel_docente_CoTeach-AI_en_espanol-1.png` | Inicio y agenda docente | Profesorado |
| `Biblioteca_de_clases_CoTeach-AI-3.png` | Biblioteca de clases | Profesorado |
| `Panel_de_aprendizaje_CoTeach-AI_en_espanol-2.png` | Inicio y aprendizaje | Alumnado |
| `Panel_de_alumno_CoTeach-AI_en_espanol-4.png` | Detalle de una clase | Alumnado |

## Objetivos y límites

- Representar fielmente su gramática visual: azul marino, azul/turquesa, superficies claras cálidas, tarjetas redondeadas y jerarquía tipográfica compacta.
- Mantener React, TypeScript, Vite y las dependencias actuales.
- Centralizar valores visuales en variables CSS y acotar los estilos por componente.
- No crear calendarios, biblioteca, recursos, reproductor, métricas ni datos ficticios mientras esas capacidades no existan.
- No modificar durante la primera historia `App.tsx`, las pantallas de subida o seguimiento, los mocks ni las pruebas que toca la Issue #48.

## Sistema de diseño

La fuente se comprobará en el entorno del frontend. Si Inter no está disponible localmente ni se carga por una fuente versionada, la pila conservará `Inter` como preferencia y usará `ui-sans-serif, system-ui, sans-serif` como fallback sin añadir una dependencia ni descargar una fuente en tiempo de ejecución.

| Grupo | Tokens iniciales |
| --- | --- |
| Tinta y superficie | `#081D45`, `#FCF9F6`, `#FFFFFF`, `#D7E0EB` |
| Acción | `#0876B9`, `#006AA4`, `#007A83` |
| Superficies suaves | `#E7F5FF`, `#E7FAF7` |
| Estados | éxito `#187A3E`, aviso `#9B5600`, error `#B82F28` |
| Geometría | escala base de 4 px; radios 12 px y 20–24 px; sombra amplia y suave |

Los degradados azul/turquesa se reservarán a la acción principal y a superficies destacadas. El contraste se verificará para cada combinación de texto, fondo, borde de foco y estado; los degradados se usarán detrás de texto blanco únicamente cuando todos los extremos cumplan AA.

## Arquitectura

La primera historia crea solamente piezas presentacionales aisladas:

```text
frontend/src/
  components/
    feedback/       InlineNotice, ProgressIndicator
    ui/             Button, Card, StatusBadge
  styles/           tokens.css, reset.css, global.css
```

Los componentes reciben datos por propiedades y no conocen API, autenticación ni rutas. La futura composición vivirá en `layouts/AppShell` y `components/navigation`, pero se crea solo cuando pueda conectarse a rutas existentes tras integrar #48. La configuración de navegación por rol será una proyección visual de rutas disponibles, nunca una regla de autorización.

## Pruebas y calidad

- Pruebas unitarias con Vitest y Testing Library para variantes, nombres accesibles y estados de los componentes.
- Prueba de contraste reproducible sobre los tokens, incluidos los extremos de cada degradado.
- `openspec validate add-frontend-design-system`, `npm run lint`, `npm run test` y `npm run build`.

## Decisiones y preguntas abiertas

- No se requiere ADR: no se modifica tecnología, proveedor, contrato ni patrón arquitectónico.
- La adscripción de la Issue #66 a una épica del roadmap queda pendiente del equipo; no afecta a la primera historia aislada.
- La integración visual de subida y seguimiento espera a que #48 entre en `dev`; así se evita sobrescribir sus estados de recepción y sus pruebas.
