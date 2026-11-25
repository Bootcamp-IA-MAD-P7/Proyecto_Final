import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";

export const worker = setupWorker(...handlers);

export const workerStartOptions = {
  onUnhandledRequest: "bypass" as const,
  serviceWorker: { url: "/mockServiceWorker.js" }
};
