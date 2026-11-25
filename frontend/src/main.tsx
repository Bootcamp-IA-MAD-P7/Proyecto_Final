import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./auth";
import { App } from "./App";
import "./styles.css";

async function enableMocks() {
  if (import.meta.env.VITE_API_MOCKS === "true") {
    const { worker, workerStartOptions } = await import("./mocks/browser");
    await worker.start(workerStartOptions);
  }
}

void enableMocks().then(() => createRoot(document.getElementById("root")!).render(
  <StrictMode><QueryClientProvider client={new QueryClient()}><BrowserRouter><AuthProvider><App /></AuthProvider></BrowserRouter></QueryClientProvider></StrictMode>
));
