export default function StatCard({ icon: Icon, label, value, hint, tone = "text-grid-teal" }) {
  return (
    <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-normal text-grid-ink">{value}</p>
        </div>
        <div className={`rounded-lg bg-slate-100 p-2.5 ${tone}`}>
          <Icon size={22} />
        </div>
      </div>
      <p className="mt-4 text-sm text-slate-500">{hint}</p>
    </div>
  );
}
