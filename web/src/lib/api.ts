import axios from "axios";

// Add type definitions for ImportMetaEnv
interface ImportMetaEnv {
  VITE_API_BASE_URL: string;
  VITE_AUTH_TOKEN?: string;
  // add other env variables as needed
}

// Augment the ImportMeta interface globally
declare global {
  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10_000,
});

api.interceptors.request.use((config) => {
  const token = import.meta.env.VITE_AUTH_TOKEN;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export type ListParams = {
  limit?: number;
  continue?: string;
  label_selector?: string;
  field_selector?: string;
  [key: string]: any;
};

export async function get<T>(url: string, params?: ListParams) {
  const res = await api.get<T>(url, { params });
  return res.data;
}
