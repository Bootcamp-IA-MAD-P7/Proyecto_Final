# ARCHITECTURE

> Cómo está construido el sistema y hacia dónde va. Mapa de documentación: [WORKFLOW](../WORKFLOW.md#2-mapa-de-documentación).

<!--
- Marca cada elemento como Actual (existe en el código), Objetivo (decidido, aún sin construir) o Candidata (por decidir).
- El porqué de las decisiones vive en los ADR, el detalle de las interfaces en CONTRACTS y el comportamiento en openspec/specs/. Aquí se resumen y se enlazan.
- Empieza con lo decidido y crece con cada funcionalidad que cambie la arquitectura: su design.md propone el cambio y las historias lo aplican aquí (WORKFLOW §2, «Qué actualizar cuando algo cambia»).
-->

## 1. Visión general

[Qué piezas forman el sistema y cómo se relacionan, en un párrafo.]

```mermaid
flowchart LR
    U[Usuario] --> A[Componente A]
    A --> B[Componente B]
```

## 2. Stack

| Área | Tecnología | Estado | Decisión |
|---|---|---|---|
| [Área] | [Tecnología] | Candidata | [ADR-0001 o —] |

## 3. Componentes

<!-- El nombre de cada componente sirve como scope en los commits (CONTRIBUTING §5). -->

| Componente | Responsabilidad | Datos que posee | Depende de | Estado |
|---|---|---|---|---|
| [Nombre] | [Qué hace y qué no hace] | [Datos] | [Componentes o servicios] | Objetivo |

## 4. Estructura del repositorio

```text
.
├── [service-a]/          # Makefile, Dockerfile (dev y prod) y .env.example propios
├── [service-b]/
├── docs/
├── openspec/
├── Makefile              # make help
├── compose.yaml          # base
├── compose.override.yaml # desarrollo
├── compose.production.yaml
└── .env.example          # variables de Compose
```

<!-- Los nombres de carpetas y archivos van en inglés (CONTRIBUTING §1). -->

## 5. Flujos principales

<!-- Un diagrama por cada flujo relevante, con sus casos de error. Enlaza el contrato de cada interfaz y, si lo hay, el design.md de la funcionalidad que lo introdujo. -->

## 6. Datos, configuración y secretos

- **Persistencia:** [Qué se guarda, dónde y durante cuánto tiempo.]
- **Configuración:** [Variables de cada componente. `.env.example` contiene solo nombres y valores inocuos.]
- **Secretos:** [Qué componente los posee. Nunca van en el cliente ni en el repositorio.]
- **Datos enviados a terceros:** [Qué se envía, a quién y cuándo.]

## 7. Entorno local y operación

<!-- Requisitos previos (Docker, make y lo que cada servicio necesite en local), puertos y qué usa cada servicio en local frente a Docker (por ejemplo, SQLite en local y PostgreSQL en Docker). Los comandos están en el Makefile (`make help`); aquí no se repiten. -->

## 8. Calidad: tests, CI y observabilidad

<!-- Herramientas de test por tipo (unitario, integración, E2E), checks del CI, logs y métricas. Los principios de testing están en AGENTS.md §2. -->

## 9. Despliegue

<!-- Dónde y cómo se despliega cada componente, qué está preparado y qué queda fuera de alcance. Desde el walking skeleton hay dos entornos desplegados (WORKFLOW §5): -->

| Entorno | Rama | Cuándo se despliega | Para qué |
|---|---|---|---|
| Pruebas | `dev` | [Al mergear en `dev`, o a mano] | Probar en la web lo integrado antes de promocionarlo |
| Producción | `main` | [Al mergear la promoción en `main`] | La versión publicada |

## 10. Decisiones y contratos

- Decisiones técnicas: [índice de ADR](ADR/README.md).
- Interfaces estables: [índice de contratos](CONTRACTS/README.md).
