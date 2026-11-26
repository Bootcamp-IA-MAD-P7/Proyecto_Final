import { expect, it } from "vitest";
import { formatAnalysisCategory, formatProcessingStage } from "./presentation";

it("localizes the processing stages returned by the API", () => {
  expect(formatProcessingStage("normalizing")).toBe("Preparando el audio");
  expect(formatProcessingStage("transcribing")).toBe("Transcribiendo");
  expect(formatProcessingStage("diarizing")).toBe("Identificando voces");
  expect(formatProcessingStage("analyzing")).toBe("Analizando el contenido");
  expect(formatProcessingStage(undefined)).toBe("En cola");
});

it("localizes pedagogical categories without changing API values", () => {
  expect(formatAnalysisCategory("vocabulary")).toBe("Vocabulario");
  expect(formatAnalysisCategory("grammar")).toBe("Gramática y construcciones");
  expect(formatAnalysisCategory("errors_corrections")).toBe("Errores y correcciones");
  expect(formatAnalysisCategory("reinforced_successes")).toBe("Aciertos reforzados");
  expect(formatAnalysisCategory("key_concepts")).toBe("Conceptos clave");
  expect(formatAnalysisCategory("resolved_questions")).toBe("Dudas resueltas");
});
