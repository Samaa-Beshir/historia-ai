import type { ChatResponse, DocumentSummary } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const message = body?.error?.message ?? `Request failed with status ${response.status}`;
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

export function postChat(question: string, era: string | null): Promise<ChatResponse> {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ question, era: era ?? undefined }),
  });
}

export function getEras(): Promise<{ eras: string[] }> {
  return request("/api/eras");
}

export function getDocuments(era?: string | null): Promise<{ documents: DocumentSummary[] }> {
  const query = era ? `?era=${encodeURIComponent(era)}` : "";
  return request(`/api/documents${query}`);
}
