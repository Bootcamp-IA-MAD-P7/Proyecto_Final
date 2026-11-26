import { Button } from "../../ui/Button/Button";
import { BrandLogo } from "../../brand/BrandLogo/BrandLogo";
import styles from "./TopBar.module.css";

interface TopBarProps {
  onSignOut: () => void;
  user: { name: string; role: "teacher" | "student" };
}

export function TopBar({ onSignOut, user }: TopBarProps) {
  const roleLabel = user.role === "teacher" ? "Profesor/a" : "Alumno/a";

  return <header className={styles.header}>
    <BrandLogo to={user.role === "teacher" ? "/upload" : "/"} />
    <div className={styles.account}>
      <span aria-hidden="true" className={styles.avatar}>{user.name.charAt(0)}</span>
      <span><strong>{user.name}</strong><small>{roleLabel}</small></span>
      <Button className={styles.signOut} onClick={onSignOut} variant="text">Salir</Button>
    </div>
  </header>;
}
