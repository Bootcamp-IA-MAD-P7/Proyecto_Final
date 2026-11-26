import { NavLink } from "react-router-dom";
import { Icon } from "../../ui/Icon/Icon";
import styles from "./RoleNavigation.module.css";

interface RoleNavigationProps { role: "teacher" | "student"; }

const roleContent = {
  teacher: { label: "Espacio docente", items: [{ label: "Subir grabación", to: "/upload" }] },
  student: { label: "Espacio del alumnado", items: [] }
} as const;

export function RoleNavigation({ role }: RoleNavigationProps) {
  const { label, items } = roleContent[role];

  return <nav aria-label="Navegación principal" className={styles.navigation}>
    <p className={styles.title}>{label}</p>
    {items.length > 0 && <ul className={styles.list}>{items.map((item) => <li key={item.to}><NavLink className={({ isActive }) => isActive ? styles.active : styles.link} to={item.to}><Icon name="upload" />{item.label}</NavLink></li>)}</ul>}
  </nav>;
}
