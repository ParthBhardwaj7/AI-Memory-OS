import axios from "axios";

// Configure backend API base URL
// FastAPI default runs on http://localhost:8000
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const memoryApi = {
  // Check if API is alive
  checkHealth: async () => {
    const response = await apiClient.get("/");
    return response.data;
  },

  // Upload PDF
  uploadPdf: async (file: File, userId: string = "default-user") => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);
    const response = await apiClient.post("/upload/pdf", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  // Upload Image
  uploadImage: async (file: File, userId: string = "default-user") => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);
    const response = await apiClient.post("/upload/image", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  // Upload Audio
  uploadAudio: async (file: File, userId: string = "default-user") => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);
    const response = await apiClient.post("/upload/audio", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  // Ingest URL link
  uploadUrl: async (url: string, userId: string = "default-user") => {
    const formData = new FormData();
    formData.append("url", url);
    formData.append("user_id", userId);
    const response = await apiClient.post("/upload/url", formData, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return response.data;
  },

  // Ask question to memory graph
  queryMemory: async (question: string, userId: string = "default-user") => {
    const response = await apiClient.post("/chat", {
      user_id: userId,
      question: question,
    });
    return response.data; // { answer: string, sources: string[] }
  },

  // Fetch categorized timeline events
  getTimeline: async (userId: string = "default-user") => {
    const response = await apiClient.get(`/timeline/${userId}`);
    return response.data;
  },

  // Fetch React Flow nodes/edges data
  getGraph: async (userId: string = "default-user") => {
    const response = await apiClient.get(`/graph/${userId}`);
    return response.data;
  },

  // Fetch Daily Digest summary
  getDailyDigest: async (userId: string = "default-user") => {
    const response = await apiClient.get(`/summary/digest/${userId}`);
    return response.data;
  },

  // Fetch overall profile summary
  getOverallSummary: async (userId: string = "default-user") => {
    const response = await apiClient.get(`/summary/all/${userId}`);
    return response.data;
  },
};
