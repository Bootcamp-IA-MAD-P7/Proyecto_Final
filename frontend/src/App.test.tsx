import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import { App } from "./App";
import { AuthProvider, demoUsers, type DemoUser } from "./auth";
import { expiredJob, expiredSubmissionHandler, receptionRejections } from "./mocks/handlers";
import { server } from "./mocks/server";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const publishedStudentResult = {
  schema_version: "0.1.0", class_id: "class-demo-01", result_version: 1,
  transcript: { speakers: [{ speaker_id: "speaker-01", participant_id: null }], segments: [{ segment_id: "segment-01", start_ms: 0, end_ms: 2000, speaker_id: "speaker-01", text: "Hoy practicamos saludos." }] },
  analysis: { general_summary: "La clase practica saludos.", items: [{ item_id: "item-01", category: "vocabulary", content: "Saludos" }] },
  review: { status: "pending", review_due_at: "2026-12-11T10:00:00Z" },
  publication: { status: "published", result_version: 1, published_at: "2026-12-10T12:00:00Z", mode: "teacher_approved" }
} as const;

function renderApp(initialEntries?: string[]) { const queryClient = new QueryClient(); const view = render(<QueryClientProvider client={queryClient}><MemoryRouter initialEntries={initialEntries}><AuthProvider><App /></AuthProvider></MemoryRouter></QueryClientProvider>); return { queryClient, ...view }; }

function renderAuthenticatedApp(user: DemoUser, initialEntries: string[], queryClient = new QueryClient()) { const view = render(<QueryClientProvider client={queryClient}><MemoryRouter initialEntries={initialEntries}><AuthProvider initialToken={`synthetic-${user.id}`} initialUser={user}><App /></AuthProvider></MemoryRouter></QueryClientProvider>); return { queryClient, ...view }; }

function signInAsDemoTeacher() { fireEvent.click(screen.getByRole("button", { name: /docente de prueba/i })); }

function uploadNamedAudio(name: string) {
  fireEvent.change(screen.getByLabelText("Audio"), { target: { files: [new File(["audio"], name, { type: "audio/mpeg" })] } });
  fireEvent.submit(screen.getByRole("button", { name: /enviar a procesar/i }).closest("form")!);
}

it("runs the synthetic teacher flow with MSW", async () => {
  renderApp();
  expect(screen.queryByText(/la autorización siempre corresponde a la API/i)).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /docente de prueba/i }));
  expect(await screen.findByRole("heading", { name: /sube una grabación/i })).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Audio"), { target: { files: [new File(["audio"], "class.mp3", { type: "audio/mpeg" })] } });
  fireEvent.submit(screen.getByRole("button", { name: /enviar a procesar/i }).closest("form")!);
  await waitFor(() => expect(screen.getByRole("heading", { name: /repaso de la clase/i })).toBeInTheDocument(), { timeout: 3000 });
  expect(screen.getByRole("heading", { name: "Transcripción" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Repaso pedagógico" })).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: /aprobar resultado/i }));
  await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent(/resultado aprobado/i));
});

it("keeps the upload form out of the student landing page", async () => {
  renderApp();
  fireEvent.click(screen.getByRole("button", { name: /estudiante de prueba/i }));
  expect(await screen.findByRole("heading", { name: /tu espacio de aprendizaje/i })).toBeInTheDocument();
  expect(screen.queryByLabelText("Audio")).not.toBeInTheDocument();
  expect(screen.getByRole("link", { name: "CoTeach-AI" })).toHaveAttribute("href", "/");
});

it("does not query results from the student landing page", async () => {
  let resultRequests = 0;
  server.use(http.get(`${apiUrl}/v1/classes/:classId/result`, () => {
    resultRequests += 1;
    return HttpResponse.json(publishedStudentResult);
  }));
  renderApp();
  fireEvent.click(screen.getByRole("button", { name: /estudiante de prueba/i }));
  expect(await screen.findByRole("heading", { name: /tu espacio de aprendizaje/i })).toBeInTheDocument();
  await new Promise((resolve) => setTimeout(resolve, 20));
  expect(resultRequests).toBe(0);
});

it("does not query a result when the route has no authenticated session", async () => {
  let resultRequests = 0;
  server.use(http.get(`${apiUrl}/v1/classes/:classId/result`, () => {
    resultRequests += 1;
    return HttpResponse.json(publishedStudentResult);
  }));
  renderApp(["/classes/class-demo-01/result"]);
  expect(await screen.findByRole("heading", { name: /tu clase, lista para repasar/i })).toBeInTheDocument();
  await new Promise((resolve) => setTimeout(resolve, 20));
  expect(resultRequests).toBe(0);
});

it("redirects a student away from the direct upload route", async () => {
  renderApp(["/upload"]);
  fireEvent.click(await screen.findByRole("button", { name: /estudiante de prueba/i }));
  expect(await screen.findByRole("heading", { name: /tu espacio de aprendizaje/i })).toBeInTheDocument();
  expect(screen.queryByLabelText("Audio")).not.toBeInTheDocument();
});

it("keeps a published result route available when the API authorizes it to a student", async () => {
  server.use(http.get(`${apiUrl}/v1/classes/class-demo-01/result`, ({ request }) => {
    if (request.headers.get("authorization") !== "Bearer synthetic-demo-student") {
      return HttpResponse.json({ error: { code: "forbidden", message: "Forbidden", retryable: false }, request_id: "request-demo-student-result" }, { status: 403 });
    }
    return HttpResponse.json(publishedStudentResult);
  }));
  renderAuthenticatedApp(demoUsers[1], ["/classes/class-demo-01/result"]);
  expect(await screen.findByRole("heading", { name: /repaso de la clase/i })).toBeInTheDocument();
  expect(screen.getByText("Vocabulario")).toBeVisible();
  expect(screen.queryByRole("button", { name: /aprobar resultado/i })).not.toBeInTheDocument();
});

it("confirms a published result without offering a redundant approval", async () => {
  server.use(http.get(`${apiUrl}/v1/classes/class-demo-01/result`, () => HttpResponse.json(publishedStudentResult)));
  renderAuthenticatedApp(demoUsers[0], ["/classes/class-demo-01/result"]);
  expect(await screen.findByRole("status")).toHaveTextContent(/resultado aprobado y publicado/i);
  expect(screen.queryByRole("button", { name: /aprobar resultado/i })).not.toBeInTheDocument();
});

it("isolates result data when switching from teacher to student", async () => {
  const authorizations: string[] = [];
  server.use(http.get(`${apiUrl}/v1/classes/class-demo-01/result`, ({ request }) => {
    authorizations.push(request.headers.get("authorization") ?? "");
    return HttpResponse.json(publishedStudentResult);
  }));
  const teacher = renderAuthenticatedApp(demoUsers[0], ["/classes/class-demo-01/result"]);
  expect(await screen.findByRole("heading", { name: /repaso de la clase/i })).toBeInTheDocument();
  expect(teacher.queryClient.getQueryData(["result", "demo-teacher", "class-demo-01"])).toBeDefined();
  fireEvent.click(screen.getByRole("button", { name: "Salir" }));
  expect(await screen.findByRole("heading", { name: /tu clase, lista para repasar/i })).toBeInTheDocument();
  await waitFor(() => expect(teacher.queryClient.getQueryData(["result", "demo-teacher", "class-demo-01"])).toBeUndefined());
  fireEvent.click(screen.getByRole("button", { name: /estudiante de prueba/i }));
  expect(await screen.findByRole("heading", { name: /tu espacio de aprendizaje/i })).toBeInTheDocument();
  expect(authorizations).toEqual(["Bearer synthetic-demo-teacher"]);
  teacher.unmount();
  renderAuthenticatedApp(demoUsers[1], ["/classes/class-demo-01/result"], teacher.queryClient);
  expect(await screen.findByRole("heading", { name: /repaso de la clase/i })).toBeInTheDocument();
  expect(authorizations).toEqual(["Bearer synthetic-demo-teacher", "Bearer synthetic-demo-student"]);
});

it("shows each processing stage only once", async () => {
  server.use(http.get(`${apiUrl}/v1/jobs/job-stage-test`, () => HttpResponse.json({ class_id: "class-demo-01", job_id: "job-stage-test", state: "analyzing", stage: "transcribing", attempt: 1, error: null })));
  renderAuthenticatedApp(demoUsers[0], ["/jobs/job-stage-test"]);
  expect(await screen.findByText("Transcribiendo")).toBeVisible();
  expect(screen.getAllByText("Transcribiendo")).toHaveLength(1);
});

it("signs in with a token of the test issuer and explains when the issuer is off", async () => {
  server.use(http.post(`${apiUrl}/dev/token`, () => HttpResponse.json({ error: { code: "resource_not_available", message: "Not available.", retryable: false }, request_id: "request-demo-05" }, { status: 404 })));
  renderApp();
  fireEvent.click(screen.getByRole("button", { name: /docente de prueba/i }));
  expect(await screen.findByRole("alert")).toHaveTextContent(/no se pudo entrar/i);
  expect(screen.queryByRole("heading", { name: /sube una grabación/i })).not.toBeInTheDocument();
});

it("keeps the existing entry and upload flow in labelled landmarks", async () => {
  renderApp();
  expect(screen.getByRole("main")).toBeInTheDocument();
  signInAsDemoTeacher();
  expect(await screen.findByRole("region", { name: /sube una grabación/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /enviar a procesar/i })).toBeEnabled();
});

it("shows the existing upload route in the teacher navigation", async () => {
  renderApp();
  signInAsDemoTeacher();
  const navigation = await screen.findByRole("navigation", { name: "Navegación principal" });
  expect(navigation).toHaveTextContent("Espacio docente");
  expect(screen.getByRole("link", { name: "Subir grabación" })).toHaveAttribute("href", "/upload");
  expect(screen.getByText("Profesor/a")).toBeVisible();
});

it("does not advertise the teacher upload action in the student navigation", async () => {
  renderApp();
  fireEvent.click(screen.getByRole("button", { name: /estudiante de prueba/i }));
  const navigation = await screen.findByRole("navigation", { name: "Navegación principal" });
  expect(navigation).toHaveTextContent("Espacio del alumnado");
  expect(screen.queryByRole("link", { name: "Subir grabación" })).not.toBeInTheDocument();
  expect(screen.getByText("Alumno/a")).toBeVisible();
});

it("offers only the audio formats admitted by the contract in the file picker", async () => {
  renderApp();
  signInAsDemoTeacher();
  const input = (await screen.findByLabelText("Audio")) as HTMLInputElement;
  for (const extension of [".ogg", ".opus", ".webm", ".mp3", ".m4a", ".mp4"]) {
    expect(input.accept).toContain(extension);
  }
});

const uiMessages: Record<string, RegExp> = {
  audio_too_large: /supera el tamaño permitido\. reduce el tamaño/i,
  unsupported_audio: /formato del audio no está admitido\. usa opus/i,
  invalid_audio_duration: /duración del audio está fuera de los límites permitidos/i
};

it.each(receptionRejections)("explains the reception error for $fileName", async ({ handler, code, message }) => {
  server.use(handler);
  renderApp();
  signInAsDemoTeacher();
  expect(await screen.findByRole("heading", { name: /sube una grabación/i })).toBeInTheDocument();
  uploadNamedAudio("class.mp3");
  const alert = await screen.findByRole("alert");
  expect(alert).toHaveTextContent(uiMessages[code]);
  expect(alert).not.toHaveTextContent(message);
  expect(screen.queryByRole("heading", { name: /repaso de la clase/i })).not.toBeInTheDocument();
});

it("explains that the audio is no longer available when the job expired", async () => {
  let jobPolls = 0;
  server.use(expiredSubmissionHandler, http.get(`${apiUrl}/v1/jobs/job-demo-expired`, () => {
    jobPolls += 1;
    return HttpResponse.json(expiredJob);
  }));
  renderApp();
  signInAsDemoTeacher();
  expect(await screen.findByRole("heading", { name: /sube una grabación/i })).toBeInTheDocument();
  uploadNamedAudio("class.mp3");
  expect(await screen.findByText(/el audio ya no está disponible/i, {}, { timeout: 3000 })).toBeInTheDocument();
  await new Promise((resolve) => setTimeout(resolve, 1800));
  expect(jobPolls).toBe(1);
  expect(screen.queryByRole("heading", { name: /repaso de la clase/i })).not.toBeInTheDocument();
});
