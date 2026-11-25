# ROADMAP

> En qué orden se construye el producto: hitos, épicas, sus funcionalidades y las dependencias entre ellas. Mapa de documentación: [WORKFLOW](../WORKFLOW.md#2-mapa-de-documentación).

<!--
- Las épicas son capacidades de producto. Cada una se especifica en una o varias funcionalidades, cada una un cambio de OpenSpec con varias historias (WORKFLOW §5). La primera épica es un walking skeleton.
- Los hitos agrupan épicas y se planifican uno cada vez; no son Issues.
- El ROADMAP llega hasta las épicas y el nombre de sus cambios de OpenSpec, que se añaden al planificar cada funcionalidad. Las historias y sus tareas viven en el tasks.md de cada cambio y en GitHub, igual que el estado y los bloqueos concretos.
- Aquí no van el alcance ni los requisitos, que están en el PRD.
- No se ponen fechas salvo por decisión expresa.
- Los IDs de planificación (E1, E2…) no son números de Issue. Al crear la Issue de una épica se añade su enlace.
-->

## Dirección

Primero, un esqueleto que se levanta en local con Docker, con el contrato v0.1, para que API, inferencia e interfaz avancen en paralelo contra él. Después, el flujo Base de extremo a extremo, una capacidad cada vez: recibir una clase, transcribirla y generar el repaso, para la presentación del 11 de diciembre; y la revisión docente con publicación y el ensayo con un lote de clases, para la del 15 de diciembre. Las fechas son las de las presentaciones ([PRD §12](PRD.md#12-restricciones-supuestos-y-riesgos)); lo que queda fuera del MVP está en el [PRD §6](PRD.md#6-alcance).

## Hito 1 — De una grabación al repaso (presentación del 11 de diciembre)

**Resultado:** una clase autorizada se sube desde la web, se procesa en local con Docker y muestra su transcripción diarizada y su repaso pedagógico.

### E1 — Walking skeleton con el contrato v0.1 · Issue: [#1](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/1)

- **Resultado:** API, worker, maintenance y web React levantados en local, con y sin Docker, con `/health`, el contrato v0.1 en [CONTRACTS](CONTRACTS/README.md) y un recorrido falso de extremo a extremo: subir un audio, ver el trabajo y consultar un resultado de ejemplo. Ver [WORKFLOW §5](../WORKFLOW.md#trabajo-por-capas). Mientras no haya servidor no se despliega ([ADR-0005](ADR/0005-local-only-environment.md)).
- **Requisitos:** RNF-01 (validación de tokens con un emisor de pruebas), RNF-03; prepara el contrato de RF-01 a RF-05 sin implementarlos.
- **Depende de:** —
- **Funcionalidades:** [`add-walking-skeleton`](../openspec/changes/add-walking-skeleton/)

### E2 — Recibir una clase y seguir su procesamiento · Issue: [#2](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/2)

- **Resultado:** el profesorado sube una grabación desde la web; el servicio la guarda de forma privada, crea un trabajo duradero, muestra su progreso y purga el audio a los 14 días.
- **Requisitos:** RF-01, RNF-02, RNF-05
- **Depende de:** E1, porque usa su estructura, su contrato y su despliegue.
- **Funcionalidades:** [`add-class-reception`](../openspec/changes/add-class-reception/)

### E3 — Transcripción diarizada consultable · Issue: [#3](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/3)

- **Resultado:** cada trabajo produce la transcripción con intervenciones por hablante y marcas temporales, y la web la muestra.
- **Requisitos:** RF-02, RF-04 (parte de transcripción), RNF-04
- **Depende de:** E2, porque transcribe los trabajos que crea. Su `explore` (medir modelos y recursos con las grabaciones autorizadas, [ARCHITECTURE §11](ARCHITECTURE.md#11-preguntas-abiertas)) puede empezar en paralelo a E1.
- **Funcionalidades:** pendiente

### E4 — Repaso pedagógico · Issue: [#4](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/4)

- **Resultado:** a partir de la transcripción se generan el repaso por categorías y el resumen general, y la web los muestra junto a la transcripción.
- **Requisitos:** RF-03, RF-04
- **Depende de:** E3, porque analiza su transcripción.
- **Funcionalidades:** pendiente

## Hito 2 — Revisión, publicación y entrega (presentación del 15 de diciembre)

**Resultado:** el profesorado revisa y publica los resultados, el alumnado autorizado solo ve lo publicado y el flujo completo se ha ensayado con un lote de clases.

### E5 — Revisión docente y publicación · Issue: [#6](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/6)

- **Resultado:** el profesorado corrige y aprueba el resultado, o este se publica solo al vencer el plazo configurado; el alumnado autorizado consulta únicamente lo publicado de su clase.
- **Requisitos:** RF-05, RNF-01
- **Depende de:** E1, porque trabaja sobre el contrato y el resultado de ejemplo; puede empezar antes del 11 en paralelo a E3 y E4. Su integración final necesita E4.
- **Funcionalidades:** pendiente

### E6 — Ensayo con un lote de clases y entrega · Issue: [#8](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/8)

- **Resultado:** un lote reducido de clases se procesa de extremo a extremo en el entorno de la demo (en local con Docker mientras no haya servidor), con tiempos, recursos y limitaciones documentados, y CoTeach recibe la guía de operación.
- **Requisitos:** RNF-04
- **Depende de:** E4 y E5, porque ensaya el flujo completo.
- **Funcionalidades:** pendiente
