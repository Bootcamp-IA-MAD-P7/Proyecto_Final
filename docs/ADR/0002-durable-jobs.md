# ADR-0002: Durable jobs in PostgreSQL

- **Estado:** Aceptado
- **Fecha:** 2026-11-24
- **Decisores:** Equipo de tres personas; CoTeach/Lay para restricciones de producto y datos.
- **Relacionado:** RF-01 a RF-05; RNF-04; ADR-0001. Sin Issue: fase 1.

## Contexto

Los trabajos largos deben sobrevivir reinicios y no bloquear publicación ni purga. La carga inicial estimada es diez clases diarias, con concurrencia aún desconocida.

## Decisión

Usar PostgreSQL 17 para persistencia y tabla de trabajos, SQLAlchemy 2 y Alembic. Reclamar trabajo con transacción corta y FOR UPDATE SKIP LOCKED. Ejecutar inferencia fuera de transacciones. En el MVP hay un único worker: al arrancar, devuelve a la cola los trabajos que quedaron en curso; no hay lease ni heartbeat. Maintenance separado publica y purga. Entrega al menos una vez, efectos idempotentes y resultados por etapa; no prometer ejecución exactamente una vez.

El detalle operativo está en [ARCHITECTURE](../ARCHITECTURE.md).

## Alternativas consideradas

- Celery con broker: solución madura para mayor escala, añade operación y coordinación DB/broker; reconsiderar si crece volumen o complejidad.
- Cola en memoria/BackgroundTasks: pierde trabajo al reiniciar.
- Lease con heartbeat y token de intento desde el MVP: necesario con varios workers, pero con uno solo añade código y pruebas sin beneficio; queda como evolución.
- SQLite local y PostgreSQL producción: divergencia en bloqueos y concurrencia.

## Consecuencias

Evita operar un broker y, con un único worker, no necesita leases; basta con reintentos de alcance pequeño y la recuperación al arrancar. Añadir un segundo worker exige antes lease con heartbeat y token de intento, con un ADR que reemplace a este. DB no disponible pausa reclamaciones/publicación y requiere recuperación; inferencia no debe monopolizar conexiones. PostgreSQL advierte que SKIP LOCKED sirve para consumidores de tablas tipo cola, no para lecturas generales consistentes: https://www.postgresql.org/docs/current/sql-select.html.
