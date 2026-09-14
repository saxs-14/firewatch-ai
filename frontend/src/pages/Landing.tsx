import { Link } from "react-router-dom";

const FEATURES = [
  { title: "Fire detection", desc: "Flags flame-coloured regions in camera footage." },
  { title: "Smoke detection", desc: "Flags low-saturation, high-texture haze regions." },
  { title: "Confidence score", desc: "Every alert carries a transparency score." },
  { title: "Configurable sensitivity", desc: "Tune how much coverage triggers an alert." },
  { title: "Alert history & evidence", desc: "Every alert is timestamped and logged." },
  { title: "Demo mode", desc: "Run on bundled sample images." },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="flex items-center justify-between px-6 py-5 max-w-6xl mx-auto">
        <div className="flex items-center gap-2 font-semibold text-lg">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-red-500" />
          FireWatch AI
        </div>
        <Link to="/app" className="rounded-lg bg-red-600 hover:bg-red-500 transition px-4 py-2 text-sm font-medium">
          Open dashboard
        </Link>
      </header>

      <main className="max-w-6xl mx-auto px-6">
        <section className="py-16 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">
            Early <span className="text-red-400">fire & smoke</span> detection from any camera
          </h1>
          <p className="mt-5 text-slate-400 max-w-2xl mx-auto text-lg">
            Upload footage and FireWatch AI flags flame- and smoke-like regions early,
            logging every alert with a confidence score.
          </p>
          <div className="mt-8 flex justify-center gap-3">
            <Link to="/app" className="rounded-lg bg-red-600 hover:bg-red-500 transition px-5 py-3 font-medium">
              Try the live demo
            </Link>
          </div>
          <p className="mt-4 text-xs font-semibold text-amber-400">
            This system is an early-warning prototype and must not replace certified fire
            detection systems.
          </p>
        </section>

        <section className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 py-8">
          {FEATURES.map((f) => (
            <div key={f.title} className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
              <h3 className="font-semibold">{f.title}</h3>
              <p className="mt-1.5 text-sm text-slate-400">{f.desc}</p>
            </div>
          ))}
        </section>

        <section className="py-16 grid sm:grid-cols-2 gap-8">
          <div>
            <h2 className="text-2xl font-bold mb-3">Who it's for</h2>
            <ul className="text-slate-400 space-y-1.5 text-sm">
              <li>Warehouses</li>
              <li>Farms</li>
              <li>Factories</li>
              <li>Schools</li>
              <li>Construction sites</li>
            </ul>
          </div>
          <div>
            <h2 className="text-2xl font-bold mb-3">Pricing model</h2>
            <ul className="text-slate-400 space-y-1.5 text-sm">
              <li>Monitoring subscription</li>
              <li>Camera + software bundle</li>
              <li>Installation service</li>
              <li>Enterprise monitoring</li>
            </ul>
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        FireWatch AI — early-warning prototype. Not certified safety equipment.
      </footer>
    </div>
  );
}
