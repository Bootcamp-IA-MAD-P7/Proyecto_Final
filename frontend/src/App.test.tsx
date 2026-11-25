import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { expect, it } from "vitest";
import { App } from "./App";
import { AuthProvider } from "./auth";
import { server } from "./mocks/server";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

function renderApp() { render(<QueryClientProvider client={new QueryClient()}><MemoryRouter><AuthProvider><App /></AuthProvider></MemoryRouter></QueryClientProvider>); }

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
