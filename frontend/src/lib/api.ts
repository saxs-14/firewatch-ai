const API_BASE = "";

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

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(await res.text().catch(() => res.statusText));
  return res.json();
}

export const api = {
  health: () => fetch(`${API_BASE}/api/health`).then((r) => json<{ status: string }>(r)),
  summary: () => fetch(`${API_BASE}/api/dashboard/summary`).then((r) => json<DashboardSummary>(r)),
  events: () => fetch(`${API_BASE}/api/events`).then((r) => json<AlertEvent[]>(r)),
  exportCsvUrl: () => `${API_BASE}/api/events/export`,
  runDemo: () => fetch(`${API_BASE}/api/analyze/demo`, { method: "POST" }).then((r) => json<AlertEvent>(r)),
  analyzeFile: (file: File) => {
    const form = new FormData();
    form.set("file", file);
    return fetch(`${API_BASE}/api/analyze`, { method: "POST", body: form }).then((r) => json<AlertEvent>(r));
  },
};
