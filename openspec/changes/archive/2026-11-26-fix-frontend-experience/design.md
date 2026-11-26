# Design

## Context

El cambio archivado `add-frontend-design-system` introdujo tokens, componentes y una primera composición, pero la validación manual revela que siguen dominando estilos del walking skeleton. Además, el inicio y las rutas de la interfaz tratan la subida como destino universal aunque la API reserva `POST /v1/classes` al profesorado.

## Goals / Non-Goals

**Goals:**

- Ajustar las pantallas existentes al lenguaje visual de los cuatro mockups sin crear las capacidades que estos ilustran.
- Crear una salida autenticada mínima para alumnado sin datos inventados ni formulario docente.
- Mostrar etapas y categorías conocidas de la API en castellano y usar un indicador indeterminado mientras la API no aporte un porcentaje real.
- Mantener accesibilidad, responsive y pruebas de los flujos existentes.

**Non-Goals:**

- No crear listas de clases, calendario, recursos, reproductor, notificaciones, filtros, métricas ni nuevas rutas de producto.
- No cambiar backend, OpenAPI, MSW ni reglas de autorización.
- No eliminar el tratamiento cliente del 403: sigue siendo una defensa ante cambios de sesión, acceso directo o respuestas del servidor.
- No archivar este cambio tras implementarlo hasta la aprobación manual posterior.

## Decisions

### Navegación de alumnado sin datos ficticios

La raíz autenticada mostrará un estado vacío honesto para alumnado cuando no haya una ruta de resultados publicada disponible. La ruta `/upload` redirigirá a esa raíz para alumnado y la marca de cabecera apuntará al destino inicial según el rol. Los resultados publicados ya autorizados por API seguirán siendo consultables por su ruta existente.

Se descarta crear un panel, lista o calendario sintético: aparentaría capacidades que el MVP aún no proporciona.

### Marca e iconografía nativas

Se implementará una marca vectorial y un conjunto mínimo de iconos SVG propios para los controles ya existentes. Evita dependencias nuevas y permite conservar color, contraste y tamaño desde tokens. No se reproducirán ilustraciones ni datos de los mockups como contenido de producto.

### Localización de valores del contrato

Las etapas y categorías se mapearán en funciones puras de presentación. La capa API seguirá usando los enums tipados y los payloads originales; los mapas solo se aplican al texto visible. El progreso será indeterminado mientras el contrato no aporte un porcentaje real; no se inferirán porcentajes a partir de la etapa.

### Corrección visual acotada

Los tokens ganarán una escala tipográfica y de distribución. `AppShell`, pantalla de acceso, tarjetas, botones, selector de archivo y progreso consumirán esa escala. Se mantendrán componentes existentes y se extraerán solo marca, iconos o campo de archivo si evitan duplicación real.

La corrección final reduce solo los espacios que no aportan separación semántica, especialmente en acceso y móvil. El selector de archivo conserva una única etiqueta accesible y pasa la acción a una nueva fila en anchuras estrechas para que el nombre de la grabación no se comprima.

### Publicación ya completada

La interfaz evaluará `publication.status` que devuelve la API. Si es `published`, mostrará la confirmación ya existente y no renderizará la acción de aprobar ni iniciará una mutación. Si no está publicado, el profesorado conserva la acción actual. Esta condición solo evita una solicitud redundante: la API sigue siendo la autoridad.

### Límite de sesión de consultas

Las consultas protegidas solo se habilitarán cuando exista un token de la sesión actual. Sus claves incluirán el identificador público de la persona, nunca el token, para que dos sesiones no compartan resultados ni errores. Al cerrar sesión, el cliente cancelará las consultas y vaciará la caché antes de retirar la identidad y el token de memoria; así, una respuesta que termine después no puede restaurar datos ni errores de la sesión anterior. La vista inicial de alumnado no consulta resultados; un resultado publicado se consulta únicamente al abrir su ruta autorizada.

## Risks / Trade-offs

- [Una persona alumna no verá contenido al iniciar] → mostrar un estado vacío explícito y conservar enlaces directos a resultados publicados autorizados.
- [Las fases API no indican progreso numérico real] → usar un indicador indeterminado y no prometer avance medido.
- [No hay archivo vectorial oficial del logotipo] → usar una marca SVG derivada de la referencia y mantenerla aislada para sustituirla cuando exista un activo oficial.

## Migration Plan

1. Añadir primero mapeos y pruebas de permisos de interfaz, etapas y categorías.
2. Integrar la composición visual y comprobar escritorio, tableta y móvil.
3. Ejecutar validaciones y revisión independiente; conservar el cambio activo para la validación manual solicitada.
