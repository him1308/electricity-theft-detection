import axios from "axios";

const defaultBaseUrl =
  typeof window === "undefined" ? "http://localhost:8000/api" : `${window.location.protocol}//${window.location.hostname}:8000/api`;

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || defaultBaseUrl
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export async function login(username, password) {
  const { data } = await api.post("/auth/login", { username, password });
  localStorage.setItem("access_token", data.access_token);
  localStorage.setItem("role", data.role);
  return data;
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("role");
}
