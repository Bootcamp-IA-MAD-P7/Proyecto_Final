# ADR-0001: Modular backend and API-first demo

- **Estado:** Aceptado
- **Fecha:** 2026-11-24
- **Decisores:** Equipo de tres personas; CoTeach/Lay para restricciones de producto y datos.
- **Relacionado:** RF-01, RF-04, RF-05; ADR-0002. Sin Issue: fase 1.

## Contexto

Tres personas necesitan desarrollar en paralelo un servicio independiente y una demostración revisable en diciembre. CoTeach conserva administración e identidades; todavía no existe contrato estable de integración.

## Decisión

Usar Python 3.11, FastAPI/Pydantic y un paquete de dominio compartido por API/worker/maintenance. Usar React con TypeScript y Vite como cliente web separado, que consume exclusivamente los endpoints REST versionados de FastAPI. Mantener revisión, autorización y reglas de negocio en el servidor. Definir primero OpenAPI y ejemplos sintéticos en fase 2, permitiendo dobles independientes. No ejecutar inferencia pesada en BackgroundTasks de la API.

El detalle operativo está en [ARCHITECTURE](../ARCHITECTURE.md).

## Alternativas consideradas

- Microservicios por modelo: despliegues y contratos innecesarios para tres personas.
- Un cliente de demostración Python acoplado: acelera una primera pantalla, pero limita la evolución de la experiencia y no comparte el tipado del contrato con un cliente web TypeScript.
- Todo dentro de FastAPI con plantillas: reduce herramientas, pero acopla la interfaz al backend y dificulta el trabajo paralelo por capas.

## Consecuencias

Separa claramente frontend y backend y permite repartir API, IA e interfaz. React, TypeScript y Vite añaden una cadena Node, construcción y pruebas propias; el contrato REST debe impedir divergencias entre ambos lados. El dominio compartido obliga a coordinar migraciones. Falta validar experiencia del equipo, versiones y dependencias. FastAPI recomienda separar computación pesada de tareas ligeras en segundo plano: https://fastapi.tiangolo.com/tutorial/background-tasks/.
