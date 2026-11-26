import type { components } from "./api/schema";

type AnalysisCategory = components["schemas"]["AnalysisCategory"];
type JobStage = components["schemas"]["JobStage"];
type Transcript = components["schemas"]["Transcript"];
type TranscriptSegment = components["schemas"]["Segment"];

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

export function formatTimestamp(milliseconds: number) {
  const totalSeconds = Math.floor(milliseconds / 1000);
  const seconds = totalSeconds % 60;
  const totalMinutes = Math.floor(totalSeconds / 60);
  const minutes = totalMinutes % 60;
  const prefix = totalMinutes >= 60 ? `${Math.floor(totalMinutes / 60)}:${String(minutes).padStart(2, "0")}` : String(minutes).padStart(2, "0");
  return `${prefix}:${String(seconds).padStart(2, "0")}`;
}

export type SpeakerIntervention = { speakerPosition: number; startMs: number; text: string };

export function groupSpeakerInterventions(transcript: Transcript): SpeakerIntervention[] {
  const speakerPositions = new Map(transcript.speakers.map((speaker, index) => [speaker.speaker_id, index + 1]));
  return transcript.segments.reduce<SpeakerIntervention[]>((interventions, segment: TranscriptSegment) => {
    const speakerPosition = speakerPositions.get(segment.speaker_id);
    const previous = interventions.at(-1);
    if (previous && previous.speakerPosition === speakerPosition) {
      previous.text = `${previous.text} ${segment.text}`;
      return interventions;
    }
    return [...interventions, { speakerPosition: speakerPosition ?? 0, startMs: segment.start_ms, text: segment.text }];
  }, []);
}
