import { createContext, useContext, useMemo, useState } from "react";

type DemoUser = { id: string; name: string; role: "teacher" | "student" };
type AuthState = { user: DemoUser | null; token: string | null; signIn: (user: DemoUser) => void; signOut: () => void };

export const demoUsers: DemoUser[] = [
  { id: "demo-teacher", name: "Docente de prueba", role: "teacher" },
  { id: "demo-student", name: "Estudiante de prueba", role: "student" }
];

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<DemoUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const value = useMemo(() => ({
    user,
    token,
    signIn(selected: DemoUser) { setUser(selected); setToken(`synthetic-${selected.id}`); },
    signOut() { setUser(null); setToken(null); }
  }), [token, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error("useAuth must be used within AuthProvider");
  return auth;
}
