import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor for error normalization
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      error.message ||
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

export interface ChatRequest {
  session_id?: string;
  message: string;
  stream?: boolean;
}

export interface SourceChunk {
  filename: string;
  chunk_preview: string;
  distance?: number;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: SourceChunk[];
  tokens_used?: number;
}

export interface UploadResponse {
  filename: string;
  chunks_indexed: number;
  status: string;
  message: string;
}

export interface HealthResponse {
  status: string;
  vector_db: string;
  documents_indexed: number;
  sources: string[];
  timestamp: string;
}

export const chatAPI = {
  sendMessage: (payload: ChatRequest) =>
    apiClient.post<ChatResponse>("/chat", payload),

  clearSession: (sessionId: string) =>
    apiClient.delete(`/chat/${sessionId}`),

  uploadDocument: (
    file: File,
    onProgress?: (percent: number) => void
  ) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post<UploadResponse>("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percent = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress(percent);
        }
      },
    });
  },

  getHealth: () => apiClient.get<HealthResponse>("/health"),
};

export const getStreamUrl = () => `${API_BASE}/chat`;

export default apiClient;
