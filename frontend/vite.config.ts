import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    // e2e/ belongs to Playwright, against the real stack (make e2e).
    include: ["src/**/*.test.{ts,tsx}"]
  }
});
