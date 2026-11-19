# PRD

> Qué producto se construye, para quién y qué debe hacer: visión, objetivos, alcance, requisitos y decisiones de producto. Mapa de documentación: [WORKFLOW](../WORKFLOW.md#2-mapa-de-documentación).

- **Nombre:** [Nombre]
- **Responsable:** [Persona o equipo]
- **Estado del documento:** Borrador

<!--
Empieza corto: una o dos frases por sección bastan para arrancar. Las secciones crecen cuando se toman decisiones.
No rellenes con suposiciones: lo que no esté confirmado va a «Preguntas abiertas».
Recoge la intención de producto, también la que todavía no está construida. Cada funcionalidad (cambio de OpenSpec) cita los IDs que cubre; el comportamiento implementado, con escenarios detallados, vive en openspec/specs/ y cita estos IDs.
Aquí no van decisiones técnicas (ARCHITECTURE y ADR), orden de trabajo (ROADMAP) ni estado (GitHub).
Los IDs no se reutilizan. Un requisito retirado se marca «Retirado» en lugar de borrarse.
-->

## 1. Resumen

[Qué es, para quién y por qué ahora, en tres o cuatro frases.]

## 2. Problema y oportunidad

- **Problema:** [Qué dificultad existe hoy.]
- **Oportunidad:** [Qué valor puede aportar el producto.]

## 3. Usuarios y partes interesadas

- **Usuarios:** [Perfiles y su necesidad principal.]
- **Partes interesadas:** [Quién revisa, mantiene o financia.]

## 4. Objetivos y criterios de éxito

<!-- Cada objetivo tiene un ID estable que citan los requisitos y una forma observable de comprobarlo. -->

| ID | Objetivo | Cómo se comprueba |
|---|---|---|
| OBJ-1 | [Resultado que se busca] | [Señal o métrica observable] |

## 5. Principios de decisión

<!-- Qué se prioriza cuando hay conflicto. Por ejemplo: control del usuario antes que automatización. -->

1. [Principio]

## 6. Alcance

### Incluido

<!-- Capacidades a alto nivel; el detalle comprobable está en los requisitos (§9 a §11). Cada capacidad suele dar una épica del ROADMAP, que se especifica en una o varias funcionalidades de OpenSpec. -->

- [Capacidad]

### Fuera de alcance

- [Exclusión y motivo]

### Futuro

<!-- Ideas sin compromiso. Solo pasan a «Incluido» con una decisión explícita. -->

- [Idea]

## 7. Glosario

| Término | Definición |
|---|---|
| [Término] | [Definición compartida] |

## 8. Flujos principales

1. [Actor → acción → resultado esperado]

## 9. Requisitos funcionales

<!-- Un requisito describe un resultado observable y no elige tecnología. -->

### RF-01 — [Resultado observable]

- **Objetivo:** OBJ-1
- **Ámbito:** Base <!-- Base: forma parte del primer producto utilizable · Evolución: ampliación prevista -->

[El sistema debe permitir…]

**Criterios de aceptación:**

- [Comportamiento observable]
- [Caso de error o alternativo]

## 10. Requisitos no funcionales

### RNF-01 — [Propiedad: usabilidad, seguridad, rendimiento, coste…]

[Condición verificable y su límite.]

**Criterios de aceptación:**

- [Medida o comprobación]

## 11. Reglas de dominio

- **RD-01:** [Regla que debe cumplirse siempre]

## 12. Restricciones, supuestos y riesgos

- **Restricciones:** [Presupuesto, plazos, plataformas, privacidad…]
- **Supuestos:** [Lo que se da por cierto y habrá que validar.]
- **Riesgos:** [Riesgo → mitigación.]

## 13. Decisiones de producto

<!-- Cada decisión de producto lleva un ID estable; las técnicas van en docs/ADR/. Una decisión no se reescribe: se marca como reemplazada y se añade la nueva. -->

| ID | Decisión | Motivo | Estado |
|---|---|---|---|
| DEC-01 | [Decisión] | [Motivo] | Aceptada |

## 14. Preguntas abiertas

<!-- Una pregunta resuelta se convierte en decisión, requisito o alcance, y se borra de aquí. -->

- [Pregunta]. Bloquea: [qué decisión o trabajo]
