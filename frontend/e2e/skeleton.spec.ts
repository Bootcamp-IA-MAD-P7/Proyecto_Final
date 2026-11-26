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
  // FakePipeline waits FAKE_STAGE_SECONDS per stage (2 by default); with 0 this step is skipped.
  await expect(page.getByText(/etapa actual: (normalizing|transcribing|diarizing|analyzing)/i)).toBeVisible();

  await expect(page.getByRole("heading", { name: /repaso de la clase/i })).toBeVisible({ timeout: 30_000 });
  await expect(page.getByRole("heading", { name: "Transcripción" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Repaso pedagógico" })).toBeVisible();

  await page.getByRole("button", { name: /aprobar resultado/i }).click();
  await expect(page.getByRole("status")).toHaveText(/resultado aprobado/i);
});

test("a teacher sees a clear error when the uploaded audio is not admitted", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /docente de prueba/i }).click();

  await expect(page.getByRole("heading", { name: /sube una grabación/i })).toBeVisible();
  // A text payload named .wav: the API rejects it by content, not by extension (contract 0.2).
  await page.getByLabel("Audio").setInputFiles({
    name: "not-audio.wav",
    mimeType: "audio/wav",
    buffer: Buffer.from("this is not an audio file"),
  });
  await page.getByRole("button", { name: /enviar a procesar/i }).click();

  await expect(page.getByRole("alert")).toHaveText(/formato del audio no está admitido/i);
  await expect(page.getByRole("heading", { name: /sube una grabación/i })).toBeVisible();
});
