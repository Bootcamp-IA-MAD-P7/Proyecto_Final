import { http, HttpResponse } from "msw";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const accepted = { class_id: "class-demo-01", job_id: "job-demo-01", state: "queued" } as const;
const result = {
  schema_version: "0.1.0", class_id: "class-demo-01", result_version: 1,
  transcript: { speakers: [{ speaker_id: "speaker-01", participant_id: null }], segments: [{ segment_id: "segment-01", start_ms: 0, end_ms: 2000, speaker_id: "speaker-01", text: "Hoy practicamos saludos." }] },
  analysis: { general_summary: "La clase practica saludos.", items: [{ item_id: "item-01", category: "vocabulary", content: "Saludos" }] },
  review: { status: "pending", review_due_at: "2026-12-11T10:00:00Z" },
  publication: { status: "unpublished", result_version: null, published_at: null, mode: null }
} as const;
export const diarizedResult = {
  ...result,
  transcript: { speakers: [{ speaker_id: "speaker-01", participant_id: null }, { speaker_id: "speaker-02", participant_id: null }], segments: [{ segment_id: "segment-01", start_ms: 62000, end_ms: 64000, speaker_id: "speaker-01", text: "Buenos" }, { segment_id: "segment-02", start_ms: 64000, end_ms: 66000, speaker_id: "speaker-01", text: "días." }, { segment_id: "segment-03", start_ms: 3723000, end_ms: 3725000, speaker_id: "speaker-02", text: "Hola." }] },
  analysis: { general_summary: "", items: [] }
} as const;
export const noVoiceResult = { ...diarizedResult, transcript: { speakers: [], segments: [] } } as const;
let polls = 0;
const classSubmitters = new Set(["Bearer synthetic-demo-teacher", "Bearer synthetic-coteach-service"]);

// Reception errors and expired job of the contract v0.2. Tests activate them with
// server.use(): openapi-fetch serializes FormData as text in jsdom, so the handler
// cannot decide from the uploaded file name here.
const reject = (code: string, message: string, status: 413 | 415 | 422) =>
  HttpResponse.json({ error: { code, message, retryable: false }, request_id: "request-demo-reception" }, { status });

export const receptionRejections = ([
  { fileName: "audio-too-large.mp3", status: 413, code: "audio_too_large", message: "El archivo excede el límite configurado en el servicio" },
  { fileName: "audio-unsupported.wav", status: 415, code: "unsupported_audio", message: "Contenido no reconocido por el servicio" },
  { fileName: "audio-too-short.mp3", status: 422, code: "invalid_audio_duration", message: "Duración no válida según la API" }
] as const).map((rejection) => ({
  ...rejection,
  handler: http.post(`${apiUrl}/v1/classes`, () => reject(rejection.code, rejection.message, rejection.status))
}));

export const expiredJob = { ...accepted, job_id: "job-demo-expired", state: "expired", stage: null, attempt: 1, error: null } as const;
export const retryWaitJob = { ...accepted, job_id: "job-demo-retry", state: "retry_wait", stage: "transcribing", attempt: 2, error: { code: "processing_unavailable", message: "El servicio de transcripción no está disponible.", retryable: true } } as const;
export const failedJob = { ...accepted, job_id: "job-demo-failed", state: "failed", stage: "diarizing", attempt: 3, error: { code: "processing_failed", message: "No se pudo identificar las voces de la grabación.", retryable: false } } as const;
export const expiredJobHandler = http.get(`${apiUrl}/v1/jobs/job-demo-expired`, () => HttpResponse.json(expiredJob));
export const expiredSubmissionHandler = http.post(`${apiUrl}/v1/classes`, () => HttpResponse.json({ ...accepted, job_id: expiredJob.job_id }, { status: 202 }));
export const retryWaitJobHandler = http.get(`${apiUrl}/v1/jobs/job-demo-retry`, () => HttpResponse.json(retryWaitJob));

export const handlers = [
  // Test issuer (spec api-access): not part of the contract, so it has no generated types.
  http.post(`${apiUrl}/dev/token`, async ({ request }) => {
    const { user } = await request.json() as { user: string };
    const role = ({ "demo-teacher": "teacher", "demo-student": "student", "coteach-service": "service" } as Record<string, string>)[user];
    if (!role) return HttpResponse.json({ error: { code: "resource_not_available", message: "Not available.", retryable: false }, request_id: "request-demo-06" }, { status: 404 });
    return HttpResponse.json({ access_token: `synthetic-${user}`, token_type: "bearer", expires_in: 3600, subject: user, role });
  }),
  http.post(`${apiUrl}/v1/classes`, ({ request }) => {
    if (!classSubmitters.has(request.headers.get("authorization") ?? "")) {
      return HttpResponse.json({ error: { code: "forbidden", message: "No tienes permiso para enviar una clase.", retryable: false }, request_id: "request-demo-04" }, { status: 403 });
    }
    polls = 0;
    return HttpResponse.json(accepted, { status: 202 });
  }),
  http.get(`${apiUrl}/v1/jobs/:jobId`, () => {
    polls += 1;
    return HttpResponse.json({ ...accepted, state: polls < 2 ? "analyzing" : "ready_for_review", stage: polls < 2 ? "analyzing" : null, attempt: 1, error: null });
  }),
  http.get(`${apiUrl}/v1/classes/:classId/result`, () => HttpResponse.json(result)),
  http.post(`${apiUrl}/v1/classes/:classId/approve`, () => HttpResponse.json({ class_id: "class-demo-01", publication: { status: "published", result_version: 1, published_at: "2026-12-10T12:00:00Z", mode: "teacher_approved" } }))
];
