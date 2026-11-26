import type { ReactNode } from "react";
import { RoleNavigation } from "../../components/navigation/RoleNavigation/RoleNavigation";
import { TopBar } from "../../components/navigation/TopBar/TopBar";
import styles from "./AppShell.module.css";

interface AppShellProps {
  children: ReactNode;
  onSignOut: () => void;
  user: { name: string; role: "teacher" | "student" };
}

export function AppShell({ children, onSignOut, user }: AppShellProps) {
  return <div className={styles.shell}>
    <TopBar onSignOut={onSignOut} user={user} />
    <div className={styles.body}>
      <RoleNavigation role={user.role} />
      <main className={styles.content}>{children}</main>
    </div>
  </div>;
}
