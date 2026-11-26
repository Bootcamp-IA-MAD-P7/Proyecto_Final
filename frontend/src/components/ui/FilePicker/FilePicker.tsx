import { useId, useState } from "react";
import { Icon } from "../Icon/Icon";
import styles from "./FilePicker.module.css";

interface FilePickerProps { accept: string; name: string; required?: boolean; }

export function FilePicker({ accept, name, required = false }: FilePickerProps) {
  const id = useId();
  const [fileName, setFileName] = useState<string>();

  return <div className={styles.field}>
    <label className={styles.label} htmlFor={id}>Audio</label>
    <label className={styles.picker} htmlFor={id}><Icon className={styles.icon} name="audio" /><span><strong>{fileName ?? "Selecciona una grabación"}</strong><small>Opus, MP3 o AAC</small></span><span className={styles.action}><Icon name="upload" /> Explorar</span></label>
    <input accept={accept} className={styles.input} id={id} name={name} onChange={(event) => setFileName(event.target.files?.[0]?.name)} required={required} type="file" />
  </div>;
}
