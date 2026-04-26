import axios from "axios";
import { getToken, clearAuth } from "./auth";

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      clearAuth();
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;

// Named helpers (used by legacy components)
export const listTickets = () => api.get("/tickets").then((r) => r.data);
export const getTicket = (id) => api.get(`/tickets/${id}`).then((r) => r.data);
export const createTicket = (body) => api.post("/tickets", body).then((r) => r.data);
export const approveTicket = (id) => api.post(`/tickets/${id}/approve`).then((r) => r.data);
export const editSendTicket = (id, finalResponse) =>
  api.post(`/tickets/${id}/edit`, { final_response: finalResponse }).then((r) => r.data);
export const rejectTicket = (id, reason = "") =>
  api.post(`/tickets/${id}/reject`, { rejection_reason: reason }).then((r) => r.data);
export const getCitations = (id) => api.get(`/tickets/${id}/citations`).then((r) => r.data);
export const getAnalytics = (window) => api.get("/analytics", { params: { window } }).then((r) => r.data);
export const listPersonas = () => api.get("/personas").then((r) => r.data);
export const updatePersona = (category, data) => api.put(`/personas/${category}`, data).then((r) => r.data);
export const listUsers = () => api.get("/users").then((r) => r.data);
export const createUser = (body) => api.post("/users", body).then((r) => r.data);
export const updateUser = (id, params) => api.patch(`/users/${id}`, null, { params }).then((r) => r.data);
