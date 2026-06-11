import { defineStore } from "pinia";
import { ref } from "vue";
import api from "../api";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(JSON.parse(localStorage.getItem("user") || "null"));
  const token = ref(localStorage.getItem("token") || "");

  function setAuth(u, t) {
    user.value = u;
    token.value = t;
    localStorage.setItem("user", JSON.stringify(u));
    localStorage.setItem("token", t);
  }

  function logout() {
    user.value = null;
    token.value = "";
    localStorage.removeItem("user");
    localStorage.removeItem("token");
  }

  async function login(username, password) {
    const { data } = await api.post("/auth/login", { username, password });
    setAuth(data.user, data.access_token);
  }

  async function register(username, password) {
    const { data } = await api.post("/auth/register", { username, password });
    setAuth(data.user, data.access_token);
  }

  return { user, token, login, register, logout };
});
