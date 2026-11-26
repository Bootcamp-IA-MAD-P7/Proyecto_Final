# Design

## Context

Ver [proposal.md](proposal.md). El contrato v0.2.0 ya contiene `Analysis`, sus seis valores de categoría y `general_summary`; no necesita campos adicionales. E3 define una interfaz `Analyzer` y mantiene la etapa `analyzing`, que hoy devuelve un análisis vacío hasta que E4 la sustituya. Sus historias #55, #56, #57 y #58 siguen abiertas, de modo que E4 no puede modificar sus secciones ni asumir que sus adaptadores ya están integrados.

`docs/ARCHITECTURE.md` exige procesar por etapas, validar el resultado antes de persistirlo, mantener los modelos locales y separar la evaluación de IA del CI. ADR-0003 propone Qwen3-8B con llama.cpp como candidato, no como decisión definitiva. El contrato no modela evidencia temporal por elemento: RF-07 queda fuera del MVP.

## Goals / Non-Goals

**Goals:**

- Evaluar candidatos mediante transcripciones sintéticas antes de acoplar uno al worker, con resultados comparables y revisión humana.
- Sustituir el análisis vacío de E3 por una salida validada del contrato, una vez seleccionado el candidato.
- Mantener un límite claro entre el texto generado y la estructura del resultado, para que una salida inválida no se persista.
- Presentar resumen y seis categorías mediante los tokens, componentes y patrones responsive de `frontend-experience` (#66).

**Non-Goals:**

- Elegir ahora un modelo, revisión, idioma, hardware, presupuesto o umbral de aceptación.
- Añadir un endpoint, modificar OpenAPI, ampliar `Analysis` con evidencias temporales o crear un módulo de vocabulario independiente.
- Resolver edición, aprobación, publicación, descubrimiento de resultados o permisos de E5.
- Enviar el audio o una transcripción a servicios externos, usar audio real en CI o versionar contenido de clases.

## Decisions

### Evaluación antes de integración

La primera historia define un conjunto pequeño de transcripciones sintéticas representativas y una rúbrica humana por categoría. Un ejecutor de evaluación recibe candidatos intercambiables y registra, fuera de datos de clase, versión/revisión, configuración, estructura válida, cobertura y precisión cualitativa de categorías, omisiones, afirmaciones no sustentadas, latencia y memoria.

Esto permite comparar el candidato de ADR-0003 con alternativas compatibles sin esperar a #55. No impone un umbral ni selecciona automáticamente: su salida es evidencia y una solicitud de decisión. Se descarta usar solo tests de esquema, porque no acreditan utilidad pedagógica.

### Adaptador de análisis y frontera de validación

Después de una selección aprobada, un adaptador de E4 implementará la interfaz `Analyzer` que E3 incorpora en `StagedPipeline`. Recibirá exclusivamente la transcripción estructurada, generará una representación intermedia limitada a resumen e ítems y la validará como `Analysis` antes de devolverla al worker. La capa que persiste el resultado solo recibe el modelo contractual validado.

Se conserva la política de E3 de modelos preparados localmente y sin descarga durante una clase. Si el adaptador falla, no carga o produce una estructura inválida, propaga el error de procesamiento aplicable; no recurre a `FakePipeline`, a otro modelo o a contenido fijo. La alternativa de validar solo al responder la API se descarta porque dejaría una versión persistida inconsistente.

### Entradas largas y texto no confiable

El adaptador transforma la transcripción en fragmentos con límites del candidato y conserva su orden y cobertura. Analiza cada fragmento como contenido no confiable, no como instrucciones operativas, y consolida resúmenes e ítems por identificadores/contenido normalizado para eliminar repeticiones sin omitir el contexto de origen. Las instrucciones incrustadas en la transcripción no pueden modificar configuración, permisos, herramientas ni el flujo del worker.

Se descarta truncar la transcripción para ajustarla al contexto porque perdería contenido relevante. También se descarta permitir que la salida del modelo controle acciones del sistema: el adaptador solo acepta el modelo `Analysis` validado.

### Integración con E3

La historia backend se apoya en la interfaz y elección de pipeline que entregue #55. Se coordina con #56 y #57, pero no toca sus adaptadores de ASR ni diarización. Respeta la política de reintentos de #58 y se completa sobre su entrada de error. La historia de integración espera además #60 para demostrar la cadena audio → transcripción → análisis; mientras tanto, las pruebas unitarias usan transcripciones sintéticas.

### Presentación web independiente

La historia frontend usa el cliente generado y MSW con resultados contractuales sintéticos. Añade una composición de resultado que coloca el resumen antes de una cuadrícula o lista de seis secciones pedagógicas; cada sección muestra ítems o un estado vacío explícito. Reutiliza `Card`, tipografía, iconografía y tokens del sistema #66, con una columna en tableta y móvil. Las claves de categoría permanecen del contrato y se localizan únicamente al renderizar.

Se descarta representar tarjetas con vocabulario, recursos, calendario u otras funciones de los mockups sin datos respaldados. La consulta, autorización, caché de sesión, transcripción y estados de revisión existentes se reutilizan sin rediseñarlos.

### Calidad y evidencia

Las pruebas automatizadas cubren estructura, categorías, fallos y composición web. La evaluación pedagógica usa una rúbrica humana acordada: exactitud/cobertura de las seis categorías cuando proceda, utilidad del resumen, omisiones y afirmaciones inventadas. La conclusión para la demo se registra separada de CI, junto con recursos y limitaciones, sin declarar aceptación mientras falten idioma y umbrales.

## Risks / Trade-offs

- [La decisión de modelo, idioma o umbral llega tarde] → Ejecutar la evaluación preliminar en paralelo y elevar la decisión con evidencia antes de comenzar la integración del adaptador.
- [La interfaz de #55 cambia durante E3] → Mantener la historia backend bloqueada por #55 y revisar el diseño antes de apply; no duplicar `Analyzer`.
- [Salida de modelo gramaticalmente válida pero pedagógicamente incorrecta] → Combinar validación de contrato con rúbrica humana, y no equiparar JSON válido con calidad.
- [Una transcripción excede el contexto o contiene instrucciones maliciosas] → Fragmentar con cobertura verificable, consolidar sin duplicados y tratar todo el texto transcrito como datos no confiables.
- [El modelo excede los recursos de la demo] → Registrar tiempo y memoria de cada candidato y mantener `processing_unavailable` como fallo explícito, sin fallback silencioso.
- [Una categoría vacía se confunde con un error] → Presentar los estados vacíos solo tras una respuesta válida, preservando los errores de consulta existentes.

## Migration Plan

1. La historia frontend puede desplegarse primero porque el contrato y MSW ya soportan `Analysis`.
2. Tras la decisión de candidato y la integración de E3, activar el adaptador de análisis en el pipeline configurado y ejecutar pruebas de regresión de resultado y fallo.
3. Ejecutar el recorrido integrado y la evaluación documentada en el equipo de demo antes de considerar E4 finalizada.
4. Si el adaptador falla en despliegue, el trabajo sigue la política de error/reintento de E3; no se migra ni se publica una versión parcial.

## Open Questions

- Qué modelo, revisión/licencia y formato de ejecución satisfacen soberanía, calidad y recursos; una elección distinta de ADR-0003 requerirá actualizar o crear el ADR correspondiente.
- En qué idioma o combinación de idiomas se redacta el repaso y si se señalan errores no corregidos en clase (PRD §14).
- Qué rúbrica, corpus autorizado y umbrales de calidad pedagógica acepta Lay para la demo (PRD §14).
- Qué equipo ejecutará la demostración y qué límite de tiempo/memoria se acepta (RNF-04).
