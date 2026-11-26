import type { components } from "../../../api/schema";
import { groupSpeakerInterventions, formatTimestamp } from "../../../presentation";
import { Card } from "../../ui/Card/Card";
import { Icon } from "../../ui/Icon/Icon";
import styles from "./TranscriptPanel.module.css";

interface TranscriptPanelProps { transcript: components["schemas"]["Transcript"]; }

export function TranscriptPanel({ transcript }: TranscriptPanelProps) {
  const interventions = groupSpeakerInterventions(transcript);
  return <Card aria-labelledby="transcript-title"><h2 id="transcript-title"><Icon name="document" />Transcripción</h2>{interventions.length === 0 ? <p className={styles.empty}>No se ha detectado voz en esta grabación.</p> : <div className={styles.interventions}>{interventions.map((intervention, index) => <article className={styles.intervention} key={`${intervention.speakerPosition}-${index}`}><p className={styles.speaker}>Hablante {intervention.speakerPosition}</p><div><time dateTime={`PT${Math.floor(intervention.startMs / 1000)}S`}>{formatTimestamp(intervention.startMs)}</time><p>{intervention.text}</p></div></article>)}</div>}</Card>;
}
