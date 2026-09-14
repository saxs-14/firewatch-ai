const API_BASE = (import.meta.env.VITE_API_BASE as string) || "https://firewatch-ai-607032555709.us-central1.run.app";
const API_KEY = (import.meta.env.VITE_API_KEY as string) || "f989500f35c07b4e61d2943d3a835b135c71e25a1ede859f";

export interface AlertEvent {
  id: number;
  source_filename: string;
  fire_detected: boolean;
  smoke_detected: boolean;
  fire_coverage_pct: number;
  smoke_coverage_pct: number;
  confidence: number;
  created_at: string;
}

export interface DashboardSummary {
  total_checks: number;
  total_alerts: number;
  fire_alerts: number;
  smoke_alerts: number;
  sensitivity_pct: number;
}

function authHeaders(): HeadersInit {
  return { "X-API-Key": API_KEY };
}

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(await res.text().catch(() => res.statusText));
  return res.json();
}

async function downloadFile(url: string, filename: string) {
  const res = await fetch(url, { headers: authHeaders() });
  if (!res.ok) throw new Error(await res.text().catch(() => res.statusText));
  const blob = await res.blob();
  const objectUrl = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = objectUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(objectUrl);
}

export const api = {
  health: () => fetch(`${API_BASE}/api/health`).then((r) => json<{ status: string }>(r)),
  summary: () =>
    fetch(`${API_BASE}/api/dashboard/summary`, { headers: authHeaders() }).then((r) => json<DashboardSummary>(r)),
  events: () => fetch(`${API_BASE}/api/events`, { headers: authHeaders() }).then((r) => json<AlertEvent[]>(r)),
  exportEvents: () => downloadFile(`${API_BASE}/api/events/export`, "firewatch_events.csv"),
  runDemo: () =>
    fetch(`${API_BASE}/api/analyze/demo`, { method: "POST", headers: authHeaders() }).then((r) =>
      json<AlertEvent>(r)
    ),
  analyzeFile: (file: File) => {
    const form = new FormData();
    form.set("file", file);
    return fetch(`${API_BASE}/api/analyze`, { method: "POST", headers: authHeaders(), body: form }).then((r) =>
      json<AlertEvent>(r)
    );
  },
};
