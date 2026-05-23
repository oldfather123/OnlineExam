import { defineStore } from "pinia";

import { login, type AppUser, type UserRole } from "@/api/users";

const STORAGE_KEY = "online-exam-user";

export const useSessionStore = defineStore("session", {
  state: () => ({
    user: null as AppUser | null,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.user),
    role: (state) => state.user?.role,
  },
  actions: {
    restore() {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) {
        return;
      }
      try {
        this.user = JSON.parse(raw) as AppUser;
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    },
    async login(role: UserRole, username: string, password: string) {
      const result = await login(role, { username, password });
      this.user = result.data;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(result.data));
    },
    logout() {
      this.user = null;
      localStorage.removeItem(STORAGE_KEY);
    },
  },
});
