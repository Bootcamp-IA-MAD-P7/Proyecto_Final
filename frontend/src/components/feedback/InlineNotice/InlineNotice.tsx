import type { ReactNode } from "react";
import styles from "./InlineNotice.module.css";

type NoticeTone = "info" | "success" | "warning" | "error";
const labels: Record<NoticeTone, string> = { info: "Información", success: "Correcto", warning: "Aviso", error: "Error" };

interface InlineNoticeProps { children: ReactNode; tone?: NoticeTone; }

export function InlineNotice({ children, tone = "info" }: InlineNoticeProps) {
  const isError = tone === "error";
  return <div aria-live={isError ? "assertive" : "polite"} className={[styles.notice, styles[tone]].join(" ")} role={isError ? "alert" : "status"}><span aria-hidden="true">{isError ? "!" : "i"}</span><div><strong>{labels[tone]}: </strong>{children}</div></div>;
}
