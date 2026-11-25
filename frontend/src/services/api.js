import axios from "axios";

const TOKEN_KEY = "supportops_access_token";
const USER_KEY = "supportops_user";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? "http://127.0.0.1:8000" : "");

const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 120000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

function getErrorMessage(error) {
  const detail = error.response?.data?.detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(", ");
  return detail || error.message || "Something went wrong";
}

export function saveAuthSession(data) {
  sessionStorage.setItem(TOKEN_KEY, data.access_token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(data.user));
}

export function clearAuthSession() {
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}

export function getSavedUser() {
  try {
    return JSON.parse(sessionStorage.getItem(USER_KEY) || "null");
  } catch {
    return null;
  }
}

export function hasAuthToken() {
  return Boolean(sessionStorage.getItem(TOKEN_KEY));
}

export async function registerCustomer(payload) {
  try {
    const response = await api.post("/api/v1/auth/register", payload);
    saveAuthSession(response.data);
    return response.data.user;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function login(payload) {
  try {
    const response = await api.post("/api/v1/auth/login", payload);
    saveAuthSession(response.data);
    return response.data.user;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function getCurrentUser() {
  try {
    const response = await api.get("/api/v1/auth/me");
    sessionStorage.setItem(USER_KEY, JSON.stringify(response.data));
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

// Tickets
export async function getTickets() {
  try {
    return (await api.get("/api/v1/tickets/")).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function createTicket(ticketData) {
  try {
    return (await api.post("/api/v1/tickets/", ticketData)).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function getTicket(ticketId) {
  try {
    return (await api.get(`/api/v1/tickets/${ticketId}`)).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function processTicket(ticketId) {
  try {
    return (await api.post(`/api/v1/agents/process-ticket/${ticketId}`)).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function uploadTicketImage(ticketId, file) {
  try {
    const formData = new FormData();
    formData.append("file", file);
    return (await api.post(`/api/v1/vision/tickets/${ticketId}/analyze`, formData)).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

// Knowledge Base (support/admin API permissions are enforced by FastAPI)
export async function getDocuments() {
  try {
    return (await api.get("/api/v1/knowledge/documents")).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function uploadDocument(file) {
  try {
    const formData = new FormData();
    formData.append("file", file);
    return (await api.post("/api/v1/knowledge/documents", formData)).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function queryKnowledge(question, topK = 4) {
  try {
    return (await api.post("/api/v1/knowledge/query", { question, top_k: topK })).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

// Approval Center (support/admin role required by FastAPI)
export async function getPendingApprovals() {
  try {
    return (await api.get("/api/v1/approvals/pending")).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function submitApprovalDecision(approvalId, decision) {
  try {
    return (await api.post(`/api/v1/approvals/${approvalId}/decision`, decision)).data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function checkBackendConnection() {
  try {
    const response = await api.get("/health");
    return { connected: true, data: response.data };
  } catch (error) {
    return { connected: false, error: getErrorMessage(error) };
  }
}

export default api;
