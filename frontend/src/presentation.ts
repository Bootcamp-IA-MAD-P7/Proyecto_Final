import type { components } from "./api/schema";

type AnalysisCategory = components["schemas"]["AnalysisCategory"];
type JobStage = components["schemas"]["JobStage"];

const stageLabels: Record<JobStage, string> = {
  normalizing: "Preparando el audio",
  transcribing: "Transcribiendo",
  diarizing: "Identificando voces",
  analyzing: "Analizando el contenido"
};

const categoryLabels: Record<AnalysisCategory, string> = {
  vocabulary: "Vocabulario",
  grammar: "Gramática y construcciones",
  errors_corrections: "Errores y correcciones",
  reinforced_successes: "Aciertos reforzados",
  key_concepts: "Conceptos clave",
  resolved_questions: "Dudas resueltas"
};

export function formatProcessingStage(stage: JobStage | null | undefined) {
  return stage ? stageLabels[stage] : "En cola";
}

export function formatAnalysisCategory(category: AnalysisCategory) {
  return categoryLabels[category];
}
