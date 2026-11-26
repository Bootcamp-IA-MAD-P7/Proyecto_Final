# Proposal

## Why

E4 del [ROADMAP](../../../docs/ROADMAP.md), épica [#4](https://github.com/Bootcamp-IA-MAD-P7/Proyecto_Final/issues/4): tras E3, una transcripción diarizada debe convertirse en un repaso útil y verificable para la clase. El resultado actual es sintético o queda vacío durante la transición de E3, por lo que todavía no demuestra RF-03 ni el objetivo de la presentación del 11 de diciembre.

## What Changes

- Generar, desde la transcripción diarizada de una clase, un resumen general y elementos de las seis categorías pedagógicas de RF-03: vocabulario, gramática y construcciones, errores y correcciones, aciertos reforzados, explicaciones o conceptos clave y dudas resueltas; las transcripciones largas se cubren por fragmentos y se consolidan sin duplicados, y su texto no confiable se trata siempre como datos.
- Mantener el resultado estructurado existente: el análisis y la transcripción siguen separados, las categorías vacías son válidas y no se añaden campos al contrato API v0.2.0.
- Separar una evaluación preliminar de candidatos de modelo, con transcripciones sintéticas y una rúbrica pedagógica, de su posterior integración técnica en el worker. La selección, el hardware y los umbrales quedan abiertos.
- Integrar el adaptador seleccionado en la etapa `analyzing` del pipeline de E3, sin producir un resultado publicable si la generación o su validación falla.
- Presentar en la web el resumen y las seis categorías con el sistema de diseño de la #66, usando el contrato y MSW sin crear un módulo independiente de vocabulario ni adelantar la revisión/publicación de E5.
- Evaluar la calidad pedagógica y los recursos de la solución sobre un corpus autorizado o sintético, de forma separada de las pruebas técnicas y sin versionar datos de clases.

## Capabilities

### New Capabilities

- `pedagogical-analysis`: generación, validación y evaluación de un repaso pedagógico estructurado a partir de una transcripción de clase (RF-03, RF-04, RNF-01, RNF-04).

### Modified Capabilities

- `frontend-experience`: presentación accesible, responsive y localizada del resumen general y de las seis categorías de análisis ya definidas por el contrato (RF-03, RF-04, RNF-01).

## Impact

- Backend y worker: interfaces de inferencia, etapa `analyzing`, validación del modelo `Analysis`, configuración de modelos y pruebas; coordina su punto de integración con las historias abiertas de E3, sin modificar sus secciones.
- Frontend React: vista de resultado, componentes presentacionales existentes y escenarios MSW, desarrollables contra `backend/openapi.json` sin cambios de OpenAPI ni de cliente generado.
- Evaluación y operación: comandos o documentación de medición compatibles con la arquitectura y ADR-0003; el corpus, el modelo definitivo, la lengua del repaso, el hardware y los umbrales requieren decisión posterior.
- Documentación afectada: este cambio OpenSpec; `docs/ROADMAP.md` se enlazará al publicarse el plan conforme a WORKFLOW §5. No cambia ADR ni contrato mientras no se elijan una tecnología o interfaz nuevas.
