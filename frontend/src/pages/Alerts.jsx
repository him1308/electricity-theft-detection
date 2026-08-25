import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import RiskBadge from "../components/RiskBadge";
import StatusPill from "../components/StatusPill";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { formatDate } from "../utils/format";

const statuses = ["New", "Under Investigation", "Verified", "Dismissed"];

export default function Alerts() {
  const { data, loading, error, setData } = useApi(async () => (await api.get("/alerts")).data, []);

  async function update(id, status) {
    const { data: updated } = await api.patch(`/alerts/${id}/status`, { status });
    setData(data.map((alert) => (alert.id === id ? updated : alert)));
  }

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-4">
      {data.length === 0 && <div className="rounded-lg border border-grid-line bg-white p-8 text-center text-slate-500">No active alerts. Train the model or upload data to generate risk alerts.</div>}
      {data.map((alert) => (
        <article key={alert.id} className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <h2 className="text-lg font-semibold text-grid-ink">{alert.consumer_id}</h2>
                <RiskBadge level={alert.risk_level} />
                <StatusPill status={alert.status} />
              </div>
              <p className="mt-3 max-w-4xl text-sm text-slate-600">{alert.reason}</p>
              <p className="mt-2 text-xs font-medium text-slate-400">{formatDate(alert.created_at)}</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="rounded-md bg-slate-100 px-3 py-2 text-sm font-bold text-grid-ink">Score {alert.risk_score}</div>
              <select value={alert.status} onChange={(event) => update(alert.id, event.target.value)} className="rounded-md border border-grid-line bg-white px-3 py-2 text-sm font-semibold">
                {statuses.map((status) => <option key={status}>{status}</option>)}
              </select>
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}
