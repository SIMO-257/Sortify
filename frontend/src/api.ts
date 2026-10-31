import type { BrowseResult, ExtensionCount, Log, LogInfo, Operation, Plan } from "./types";

// The token arrives in the URL fragment (never sent to a server) and is kept for the tab.
function loadToken(): string {
  const fromUrl = new URLSearchParams(window.location.hash.slice(1)).get("token");
  try {
    if (fromUrl) {
      sessionStorage.setItem("sortify-token", fromUrl);
      history.replaceState(null, "", window.location.pathname);
      return fromUrl;
    }
    return sessionStorage.getItem("sortify-token") ?? "";
  } catch {
    return fromUrl ?? "";
  }
}

const token = loadToken();

export function hasToken(): boolean {
  return token !== "";
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", "X-Sortify-Token": token },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = body?.detail;
    throw new Error(typeof detail === "string" ? detail : `Request failed (${response.status})`);
  }
  return body as T;
}

const post = (body: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(body) });
const query = (params: Record<string, string | boolean>) =>
  new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)])).toString();

export const api = {
  operations: () => request<Operation[]>("/api/operations"),
  extensions: (folder: string, recursive: boolean) =>
    request<ExtensionCount[]>(`/api/extensions?${query({ folder, recursive })}`),
  plan: (operation: string, folder: string, options: Record<string, unknown>) =>
    request<Plan>("/api/plan", post({ operation, folder, options })),
  apply: (plan_id: string, action_ids: number[], confirm?: string) =>
    request<Log>("/api/apply", post({ plan_id, action_ids, confirm })),
  logs: () => request<LogInfo[]>("/api/logs"),
  log: (id: string) => request<Log>(`/api/logs/${id}`),
  undo: (id: string) => request<Log>(`/api/logs/${id}/undo`, { method: "POST" }),
  browse: (path: string, hidden: boolean) =>
    request<BrowseResult>(`/api/fs/browse?${query({ path, hidden })}`),
};
