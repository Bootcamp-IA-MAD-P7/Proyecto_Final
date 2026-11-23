# ADR-0001: Modular backend and API-first demo

- **Estado:** Propuesto
- **Fecha:** 2026-11-23
- **Decisores:** Equipo de tres personas; CoTeach/Lay para restricciones de producto y datos.
- **Relacionado:** RF-01, RF-04, RF-05; ADR-0002. Sin Issue: propuesta de fase 1.

## Contexto

Tres personas necesitan desarrollar en paralelo un servicio independiente y una demostración revisable en diciembre. CoTeach conserva administración e identidades; todavía no existe contrato estable de integración.

## Decisión

Proponer Python 3.11, FastAPI/Pydantic, un paquete de dominio compartido por API/worker/maintenance y Streamlit como cliente de API. Mantener revisión y autorización en servidor. Definir primero OpenAPI y ejemplos sintéticos en fase 2, permitiendo mocks independientes. No ejecutar inferencia pesada en BackgroundTasks de la API.

La propuesta requiere aprobación humana antes de pasar a Aceptado. El detalle operativo está en [ARCHITECTURE](../ARCHITECTURE.md).

## Alternativas consideradas

- Microservicios por modelo: despliegues y contratos innecesarios para tres personas.
- Todo dentro de Streamlit: acopla integración, permisos e inferencia a la demostración.
- SPA con frontend separado: válida, pero añade otra cadena de herramientas; reconsiderar al evolucionar la interfaz.

## Consecuencias

Reduce integración y permite repartir API, IA e interfaz. El dominio compartido obliga a coordinar migraciones; Streamlit limita UX compleja. Falta validar experiencia del equipo y dependencias. FastAPI recomienda separar computación pesada de tareas ligeras en segundo plano: https://fastapi.tiangolo.com/tutorial/background-tasks/.
