import { defineConfig, devices } from "@playwright/test";

// End-to-end tests against the real stack of `make up` (design of add-walking-skeleton).
// They run locally with `make e2e`, not in CI, so the CI image carries no browsers.
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  retries: 0,
  reporter: "list",
  use: {
    baseURL: process.env.E2E_BASE_URL || `http://localhost:${process.env.FRONTEND_PORT || "5173"}`,
    trace: "retain-on-failure"
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }]
});
