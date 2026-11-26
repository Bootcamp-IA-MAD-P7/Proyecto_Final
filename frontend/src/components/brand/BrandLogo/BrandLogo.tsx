import { Link } from "react-router-dom";
import styles from "./BrandLogo.module.css";

interface BrandLogoProps { to: string; }

export function BrandLogo({ to }: BrandLogoProps) {
  return <Link aria-label="CoTeach-AI" className={styles.brand} to={to}><svg aria-hidden="true" className={styles.mark} viewBox="0 0 32 32"><path d="M5 7h13a7 7 0 0 1 0 14H12l-5 4v-5a7 7 0 0 1-2-13Z" /><path d="M18 12h5a6 6 0 0 1 0 12h-3l-4 3v-4" /></svg><span>CoTeach-AI</span></Link>;
}
