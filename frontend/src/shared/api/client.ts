import { env } from "../config/env";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

/** V12 — set once by AuthContext on every session change. Every request
 * below attaches it as a bearer token when present; the backend verifies
 * it and rejects anything that doesn't match the path's student_id. */
let authToken: string | null = null;

export function setAuthToken(token: string | null): void {
  authToken = token;
}

function authHeaders(): Record<string, string> {
  return authToken ? { Authorization: `Bearer ${authToken}` } : {};
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    headers: { "Content-Type": "application/json", ...authHeaders() },
    ...init,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(response.status, body || response.statusText);
  }

  return (await response.json()) as T;
}

/** No forced Content-Type here — the browser sets the correct multipart
 * boundary itself when the body is a FormData (V8, Document Intelligence). */
async function requestForm<T>(path: string, formData: FormData): Promise<T> {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    method: "POST", body: formData, headers: authHeaders(),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new ApiError(response.status, body || response.statusText);
  }

  return (await response.json()) as T;
}

export const apiClient = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  postForm: <T>(path: string, formData: FormData) => requestForm<T>(path, formData),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
