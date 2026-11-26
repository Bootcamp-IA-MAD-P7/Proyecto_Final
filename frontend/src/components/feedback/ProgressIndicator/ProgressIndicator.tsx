import styles from "./ProgressIndicator.module.css";

interface ProgressIndicatorProps { label: string; value: number; }

export function ProgressIndicator({ label, value }: ProgressIndicatorProps) {
  const boundedValue = Math.min(100, Math.max(0, value));
  return <div className={styles.container}><div className={styles.label}><span>{label}</span><span>{boundedValue}%</span></div><progress aria-label={label} className={styles.progress} max={100} value={boundedValue} /></div>;
}
