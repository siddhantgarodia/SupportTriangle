import { useState, useCallback } from "react";
import { getUser, saveAuth, clearAuth } from "../auth";
import api from "../api";

export function useAuth() {
  const [user, setUser] = useState(getUser);

  const login = useCallback(async (email, password) => {
    const params = new URLSearchParams();
    params.append("username", email);
    params.append("password", password);
    const { data } = await api.post("/auth/login", params, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    saveAuth(data.access_token, data.user);
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setUser(null);
  }, []);

  return { user, login, logout };
}
