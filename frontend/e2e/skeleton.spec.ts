import { fileURLToPath } from "node:url";
import { expect, test } from "@playwright/test";

// 61 seconds of a synthetic tone in Opus: real audio above the shortest duration accepted.
const audio = fileURLToPath(new URL("./fixtures/synthetic-class.ogg", import.meta.url));

test("a teacher signs in, uploads a class, follows its progress and sees the result", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /docente de prueba/i }).click();

  await expect(page.getByRole("heading", { name: /sube una grabación/i })).toBeVisible();
  await page.getByLabel("Audio").setInputFiles(audio);
  await page.getByRole("button", { name: /enviar a procesar/i }).click();

  await expect(page.getByRole("heading", { name: /estamos preparando el repaso/i })).toBeVisible();
  await expect(page.getByText(/etapa actual: (normalizing|transcribing|diarizing|analyzing)/i)).toBeVisible();

  await expect(page.getByRole("heading", { name: /repaso de la clase/i })).toBeVisible({ timeout: 30_000 });
  await expect(page.getByRole("heading", { name: "Transcripción" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Repaso pedagógico" })).toBeVisible();

  await page.getByRole("button", { name: /aprobar resultado/i }).click();
  await expect(page.getByRole("status")).toHaveText(/resultado aprobado/i);
});
