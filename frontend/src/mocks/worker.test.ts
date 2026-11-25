import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

describe("MSW Service Worker", () => {
  it("ships the worker script in Vite's public directory", async () => {
    const script = await readFile(resolve(process.cwd(), "public/mockServiceWorker.js"), "utf8");
    expect(script).toContain("Mock Service Worker");
  });
});
