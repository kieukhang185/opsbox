import axios from "axios";

// Add type definitions for ImportMetaEnv
interface ImportMetaEnv {
  VITE_API_BASE_URL: string;
  VITE_AUTH_TOKEN?: string;
  VITE_API_BASE_WS_URL?: string;
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

export type ListResponse<T> = { items: T[]; continue?: string; total?: number };

export async function list<T>(
  url: string,
  params?: ListParams,
): Promise<ListResponse<T>> {
  const res = await api.get(url, { params });
  const data = res.data;
  if (Array.isArray(data)) return { items: data };
  return data as ListResponse<T>;
}

/** Count items across pages (bounded to avoid overload). */
export async function listAllCount(
  url: string,
  params?: Omit<ListParams, "continue">,
  safety = { maxPages: 10, pageSize: 200 },
) {
  let token: string | undefined = undefined;
  let pages = 0;
  let total = 0;
  do {
    const resp: ListResponse<any> = await list<any>(url, {
      ...params,
      limit: safety.pageSize,
      continue: token,
    });
    total += resp.items?.length ?? 0;
    token = resp.continue;
    pages += 1;
  } while (token && pages < safety.maxPages);
  return total;
}
