import { defineStore } from "pinia";
import api from "../api/axios";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: null,
  }),

  actions: {
    setToken(token) {
      this.token = token;
      if (token) {
        localStorage.setItem("token", token);
        api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      } else {
        localStorage.removeItem("token");
        delete api.defaults.headers.common["Authorization"];
      }
    },

    async login(email, password) {
      const res = await api.post("/auth/login", { email, password });
      const { access_token } = res.data;

      this.setToken(access_token);

      const me = await api.get("/auth/me");
      this.user = me.data;

      return this.user;
    },

    async fetchMe() {
      if (!this.token) return null;
      api.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
      const res = await api.get("/auth/me");
      this.user = res.data;
      return this.user;
    },

    async logout() {
      this.setToken(null);
      this.user = null;
    },
  },
});
