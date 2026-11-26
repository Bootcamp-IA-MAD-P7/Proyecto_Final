import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import { App } from "./App";
import { AuthProvider } from "./auth";
import { expiredJob, expiredSubmissionHandler, receptionRejections } from "./mocks/handlers";
import { server } from "./mocks/server";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function renderApp() { render(<QueryClientProvider client={new QueryClient()}><MemoryRouter><AuthProvider><App /></AuthProvider></MemoryRouter></QueryClientProvider>); }

function signInAsDemoTeacher() { fireEvent.click(screen.getByRole("button", { name: /docente de prueba/i })); }

function uploadNamedAudio(name: string) {
  fireEvent.change(screen.getByLabelText("Audio"), { target: { files: [new File(["audio"], name, { type: "audio/mpeg" })] } });
  fireEvent.submit(screen.getByRole("button", { name: /enviar a procesar/i }).closest("form")!);
}

it("runs the synthetic teacher flow with MSW", async () => {
  renderApp();
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

it("keeps the upload screen unauthoritative and explains a 403 denial to a student", async () => {
  renderApp();
  fireEvent.click(screen.getByRole("button", { name: /estudiante de prueba/i }));
  expect(await screen.findByRole("heading", { name: /sube una grabación/i })).toBeInTheDocument();
  fireEvent.change(screen.getByLabelText("Audio"), { target: { files: [new File(["audio"], "class.mp3", { type: "audio/mpeg" })] } });
  fireEvent.submit(screen.getByRole("button", { name: /enviar a procesar/i }).closest("form")!);
  await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("No tienes permisos para subir grabaciones. Esta acción está reservada al profesorado"));
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
