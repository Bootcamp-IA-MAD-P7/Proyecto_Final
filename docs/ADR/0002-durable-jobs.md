# ADR-0002: Durable jobs in PostgreSQL

- **Estado:** Propuesto
- **Fecha:** 2026-11-23
- **Decisores:** Equipo de tres personas; CoTeach/Lay para restricciones de producto y datos.
- **Relacionado:** RF-01 a RF-05; RNF-04; ADR-0001. Sin Issue: propuesta de fase 1.

## Contexto

Los trabajos largos deben sobrevivir reinicios y no bloquear publicación ni purga. La carga inicial estimada es diez clases diarias, con concurrencia aún desconocida.

## Decisión

Proponer PostgreSQL 17 para persistencia y tabla de trabajos, SQLAlchemy 2 y Alembic. Reclamar trabajo con transacción corta y FOR UPDATE SKIP LOCKED; lease, heartbeat y token de intento impiden escritura tardía. Ejecutar inferencia fuera de transacciones. Maintenance separado recupera abandonados y publica/purga. Entrega al menos una vez, efectos idempotentes y resultados por etapa; no prometer ejecución exactamente una vez.

La propuesta requiere aprobación humana antes de pasar a Aceptado. El detalle operativo está en [ARCHITECTURE](../ARCHITECTURE.md).

## Alternativas consideradas

- Celery con broker: solución madura para mayor escala, añade operación y coordinación DB/broker; reconsiderar si crece volumen o complejidad.
- Cola en memoria/BackgroundTasks: pierde trabajo al reiniciar.
- SQLite local y PostgreSQL producción: divergencia en bloqueos y concurrencia.

## Consecuencias

Evita operar un broker, pero exige implementar y probar leases/reintentos de alcance pequeño. DB no disponible pausa reclamaciones/publicación y requiere recuperación; inferencia no debe monopolizar conexiones. PostgreSQL advierte que SKIP LOCKED sirve para consumidores de tablas tipo cola, no para lecturas generales consistentes: https://www.postgresql.org/docs/current/sql-select.html.
