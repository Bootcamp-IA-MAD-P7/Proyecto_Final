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
let polls = 0;
const classSubmitters = new Set(["Bearer synthetic-demo-teacher", "Bearer synthetic-coteach-service"]);

export const handlers = [
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
