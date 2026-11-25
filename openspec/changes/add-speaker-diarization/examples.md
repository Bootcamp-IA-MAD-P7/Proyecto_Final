# Ejemplos sintéticos

Ejemplos del contrato 0.1.0 para la diarización, sin credenciales ni datos personales reales. Audio simulado, no incluido. Referencia: [diseño](design.md) y [spec](specs/diarization/spec.md).

Todas las peticiones a `/v1` llevan `Authorization: Bearer <token>`. En local, el token lo emite el emisor de pruebas para un usuario sintético; no se incluye ninguno aquí.

## Resultado con transcripción diarizada

GET /v1/classes/class-demo-01/result → 200 (tras completar la etapa `DIARIZING`):

```json
{
  "schema_version":"0.1.0",
  "class_id":"class-demo-01",
  "result_version":1,
  "transcript":{
    "speakers":[
      {"speaker_id":"speaker-01","participant_id":"demo-teacher"},
      {"speaker_id":"speaker-02","participant_id":null}
    ],
    "segments":[
      {"segment_id":"segment-01","start_ms":0,"end_ms":2500,"speaker_id":"speaker-01","text":"Hoy practicamos saludos."},
      {"segment_id":"segment-02","start_ms":2600,"end_ms":5200,"speaker_id":"speaker-02","text":"Buenos días a todos."},
      {"segment_id":"segment-03","start_ms":5300,"end_ms":7800,"speaker_id":"speaker-01","text":"Vamos a repasar el vocabulario."}
    ]
  },
  "analysis":{
    "general_summary":"La clase practica saludos y vocabulario.",
    "items":[{"item_id":"item-01","category":"vocabulary","content":"Saludos y presentaciones"}]
  },
  "review":{"status":"pending","review_due_at":"2026-12-11T10:00:00Z"},
  "publication":{"status":"unpublished","result_version":null,"published_at":null,"mode":null}
}
```

`speaker-02` tiene `participant_id: null` porque no se pudo asociar a un participante de la clase; la edición de esa asociación pertenece a la historia 017.

## Errores de diarización

422 por audio inválido:

```json
{"error":{"code":"invalid_audio","message":"El audio no es válido para diarización","retryable":false},"request_id":"request-demo-05"}
```

500 por fallo de procesamiento:

```json
{"error":{"code":"processing_failed","message":"La etapa de diarización falló","retryable":true},"request_id":"request-demo-06"}
```

Otros casos usan el mismo sobre: 401 `unauthenticated`, 403 `forbidden`, 404 `resource_not_available`, 409 `result_not_ready`, 503 `service_unavailable`.
