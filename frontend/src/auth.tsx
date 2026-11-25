import { createContext, useContext, useMemo, useState } from "react";
import { baseUrl } from "./api/client";

type DemoUser = { id: string; name: string; role: "teacher" | "student" };
type AuthState = { user: DemoUser | null; token: string | null; signIn: (user: DemoUser) => Promise<void>; signOut: () => void };

export const demoUsers: DemoUser[] = [
  { id: "demo-teacher", name: "Docente de prueba", role: "teacher" },
  { id: "demo-student", name: "Estudiante de prueba", role: "student" }
];

/** Token of the test issuer POST /dev/token (spec api-access), only for synthetic users. */
async function requestDevToken(user: string): Promise<string> {
  const response = await fetch(`${baseUrl}/dev/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user })
  });
  if (!response.ok) throw new Error(`Test issuer answered ${response.status}`);
  const { access_token } = await response.json() as { access_token: string };
  return access_token;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<DemoUser | null>(null);
  // Only in memory: the token is lost when the page is reloaded (design of add-walking-skeleton).
  const [token, setToken] = useState<string | null>(null);
  const value = useMemo(() => ({
    user,
    token,
    async signIn(selected: DemoUser) { const issued = await requestDevToken(selected.id); setToken(issued); setUser(selected); },
    signOut() { setUser(null); setToken(null); }
  }), [token, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error("useAuth must be used within AuthProvider");
  return auth;
}
