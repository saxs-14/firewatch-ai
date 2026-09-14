import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import { api, DashboardSummary, AlertEvent } from "../lib/api";
import KpiCard from "../components/KpiCard";

export default function Dashboard() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [events, setEvents] = useState<AlertEvent[]>([]);
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<AlertEvent | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [s, e] = await Promise.all([api.summary(), api.events()]);
      setSummary(s);
      setEvents(e);
    } catch {
      /* offline */
    }
  }, []);

  useEffect(() => {
    api.health().then(() => setApiOnline(true)).catch(() => setApiOnline(false));
    refresh();
  }, [refresh]);

  const runDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      setLastResult(await api.runDemo());
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  const runUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      setLastResult(await api.analyzeFile(file));
      setFile(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-red-500" />
          FireWatch AI
        </Link>
        <span className="flex items-center gap-2 text-xs">
          <span className={`inline-block h-2 w-2 rounded-full ${apiOnline ? "bg-emerald-500" : "bg-red-500"}`} />
          {apiOnline === null ? "Checking..." : apiOnline ? "Backend online" : "Backend offline"}
        </span>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {!apiOnline && apiOnline !== null && (
          <div className="rounded-lg border border-red-500/40 bg-red-500/10 p-4 text-sm">
            Can't reach the backend at <code>/api</code>. Start it with <code>uvicorn app.main:app --reload</code>.
          </div>
        )}

        <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <h2 className="font-semibold mb-4">Check footage</h2>
          <div className="flex flex-wrap items-center gap-3">
            <input
              type="file"
              accept="image/*,video/*"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-slate-800 file:px-3 file:py-2 file:text-slate-200"
            />
            <button
              disabled={!file || loading}
              onClick={runUpload}
              className="rounded-lg bg-red-600 hover:bg-red-500 disabled:opacity-40 transition px-4 py-2 text-sm font-medium"
            >
              {loading ? "Analyzing..." : "Analyze upload"}
            </button>
            <span className="text-slate-500 text-sm">or</span>
            <button
              disabled={loading}
              onClick={runDemo}
              className="rounded-lg border border-slate-700 hover:border-slate-500 disabled:opacity-40 transition px-4 py-2 text-sm font-medium"
            >
              {loading ? "Running..." : "Run demo sample"}
            </button>
          </div>
          {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
          {lastResult && (
            <p className="mt-4 text-sm">
              {lastResult.fire_detected || lastResult.smoke_detected ? (
                <span className="text-red-400 font-semibold">
                  Alert: {lastResult.fire_detected ? "fire" : ""}
                  {lastResult.fire_detected && lastResult.smoke_detected ? " + " : ""}
                  {lastResult.smoke_detected ? "smoke" : ""} detected (confidence {lastResult.confidence})
                </span>
              ) : (
                <span className="text-emerald-400">No fire or smoke detected.</span>
              )}
            </p>
          )}
        </section>

        <section className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label="Total checks" value={summary?.total_checks ?? "-"} />
          <KpiCard label="Total alerts" value={summary?.total_alerts ?? "-"} accent="alert" />
          <KpiCard label="Fire alerts" value={summary?.fire_alerts ?? "-"} accent="alert" />
          <KpiCard label="Smoke alerts" value={summary?.smoke_alerts ?? "-"} />
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold">Alert history</h2>
            <button onClick={() => api.exportEvents()} className="text-sm rounded-lg border border-slate-700 hover:border-slate-500 transition px-3 py-1.5">
              Export CSV
            </button>
          </div>
          {events.length === 0 ? (
            <p className="text-sm text-slate-500">No checks yet — run the demo or upload footage above.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-800">
                  <th className="py-2 pr-4">File</th>
                  <th className="py-2 pr-4">Fire</th>
                  <th className="py-2 pr-4">Smoke</th>
                  <th className="py-2 pr-4">Confidence</th>
                  <th className="py-2 pr-4">Time</th>
                </tr>
              </thead>
              <tbody>
                {events.map((e) => (
                  <tr key={e.id} className="border-b border-slate-800/60">
                    <td className="py-2 pr-4">{e.source_filename}</td>
                    <td className="py-2 pr-4">{e.fire_detected ? <span className="text-red-400">Yes</span> : "No"}</td>
                    <td className="py-2 pr-4">{e.smoke_detected ? <span className="text-amber-400">Yes</span> : "No"}</td>
                    <td className="py-2 pr-4">{e.confidence}</td>
                    <td className="py-2 pr-4 text-slate-500">{new Date(e.created_at).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}
