
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 120000,
});

function getErrorMessage(error) {
  const detail = error.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }

  return detail || error.message || "Something went wrong";
}

// Tickets
export async function getTickets() {
  try {
    const response = await api.get("/api/v1/tickets/");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function createTicket(ticketData) {
  try {
    const response = await api.post("/api/v1/tickets/", ticketData);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function getTicket(ticketId) {
  try {
    const response = await api.get(`/api/v1/tickets/${ticketId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function processTicket(ticketId) {
  try {
    const response = await api.post(
      `/api/v1/agents/process-ticket/${ticketId}`
    );
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

// Knowledge Base
export async function getDocuments() {
  try {
    const response = await api.get("/api/v1/knowledge/documents");
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function uploadDocument(file) {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post(
      "/api/v1/knowledge/documents",
      formData
    );

    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

export async function queryKnowledge(question, topK = 4) {
  try {
    const response = await api.post("/api/v1/knowledge/query", {
      question,
      top_k: topK,
    });

    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
}

// Backend connection
export async function checkBackendConnection() {
  try {
    const response = await api.get("/health");

    return {
      connected: true,
      data: response.data,
    };
  } catch (error) {
    return {
      connected: false,
      error: getErrorMessage(error),
    };
  }
}

export default api;

export async function loginApprovals(apiKey) {
  const response = await api.post(
    "/api/v1/approvals/session",
    { api_key: apiKey },
    { withCredentials: true }
  );

  return response.data;
}

export async function logoutApprovals() {
  const response = await api.delete(
    "/api/v1/approvals/session",
    { withCredentials: true }
  );

  return response.data;
}

export async function getPendingApprovals() {
  const response = await api.get(
    "/api/v1/approvals/admin/pending",
    { withCredentials: true }
  );

  return response.data;
}

export async function submitApprovalDecision(approvalId, decision) {
  const response = await api.post(
    `/api/v1/approvals/admin/${approvalId}/decision`,
    decision,
    { withCredentials: true }
  );

  return response.data;
}