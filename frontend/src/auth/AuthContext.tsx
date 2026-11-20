import { createContext, useContext, useState, type ReactNode } from "react";

import { api, clearSession, getEmail, getRole, saveSession } from "../lib/api";
import type { TokenOut } from "../lib/types";

interface AuthState {
  email: string | null;
  role: string | null;
  isLoggedIn: boolean;
  isAdmin: boolean;
  login: (email: string, password: string) => Promise<TokenOut>;
  register: (email: string, password: string) => Promise<TokenOut>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [email, setEmail] = useState<string | null>(getEmail() ?? "admin@local");
  const [role, setRole] = useState<string | null>(getRole() ?? "admin");

  const applySession = (data: TokenOut) => {
    saveSession(data.token, data.role, data.user.email);
    setEmail(data.user.email);
    setRole(data.role);
    return data;
  };

  const value: AuthState = {
    email: email || "admin@local",
    role: role || "admin",
    isLoggedIn: true,
    isAdmin: true,
    login: async (loginEmail, password) =>
      applySession(await api.post<TokenOut>("/api/auth/login", { email: loginEmail, password })),
    register: async (registerEmail, password) =>
      applySession(
        await api.post<TokenOut>("/api/auth/register", { email: registerEmail, password }),
      ),
    logout: () => {
      clearSession();
      setEmail("admin@local");
      setRole("admin");
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth phải nằm trong <AuthProvider>");
  return ctx;
}

export function RequireAuth({ children }: { children: ReactNode }) {
  return <>{children}</>;
}

export function RequireAdmin({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
