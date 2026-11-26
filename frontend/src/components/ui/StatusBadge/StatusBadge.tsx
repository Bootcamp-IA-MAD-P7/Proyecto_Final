import type { ReactNode } from "react";
import styles from "./StatusBadge.module.css";

type StatusTone = "success" | "warning" | "danger" | "info";
const symbols: Record<StatusTone, string> = { success: "✓", warning: "!", danger: "!", info: "i" };

interface StatusBadgeProps { children: ReactNode; tone?: StatusTone; }

export function StatusBadge({ children, tone = "info" }: StatusBadgeProps) {
  return <span className={[styles.badge, styles[tone]].join(" ")} role="status"><span aria-hidden="true">{symbols[tone]}</span>{children}</span>;
}
