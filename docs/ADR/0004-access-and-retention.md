# ADR-0004: Private storage and controlled publication

- **Estado:** Propuesto
- **Fecha:** 2026-11-23
- **Decisores:** Equipo de tres personas; CoTeach/Lay para restricciones de producto y datos.
- **Relacionado:** RF-01, RF-04, RF-05; RNF-01, RNF-02; ADR-0002. Sin Issue: propuesta de fase 1.

## Contexto

El PRD limita audio a 14 días y acceso a participantes autorizados. Las 24 horas de revisión son provisionales; no están definidos consentimiento completo, retención de derivados ni contrato de identidad.

## Decisión

Proponer volumen privado de audio en servidor propio, DB independiente de Odoo y acceso exclusivamente por API autorizada. Tokens de vida corta verificados y pertenencia a clase resuelta por servidor. Original y temporales fuera de Git y de backups; vencimiento bloquea lecturas y activa borrado reintentable. Versionar resultados/correcciones; aprobar y publicar automáticamente usan la misma transición transaccional. Proponer contar revisión desde disponibilidad del resultado y no publicar borradores in_review sin aprobación: ambos detalles requieren validación de Lay.

La propuesta requiere aprobación humana antes de pasar a Aceptado. El detalle operativo está en [ARCHITECTURE](../ARCHITECTURE.md).

## Alternativas consideradas

- Enlaces públicos de audio/resultados: no aseguran pertenencia a clase ni revocación.
- Almacenamiento S3 desde el inicio: válido al distribuir workers, añade operación para el primer host; mantener interfaz sustituible.
- Copiar usuarios/contraseñas de Odoo: duplica responsabilidad; acordar integración de identidad.

## Consecuencias

Reduce superficie expuesta y facilita purga, con límite de disponibilidad de un host. Un backend caído no puede garantizar borrado físico puntual: bloquear al reiniciar, purgar antes de reanudar y acordar tolerancia. Snapshots externos pueden incumplir retención; hay que excluir audios y verificarlo. Consentimiento y retención de derivados pendientes impiden declarar listo el tratamiento real en producción. Demo sintética puede avanzar con emisor de pruebas aislado. No fija proveedor ni política legal nueva.
