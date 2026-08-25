import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";

export default function Analytics() {
  const { data, loading, error } = useApi(async () => (await api.get("/dashboard/summary")).data, []);
  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const riskData = Object.entries(data.risk_distribution).map(([risk, count]) => ({ risk, count }));

  return (
    <div className="grid gap-6 xl:grid-cols-2">
      <section className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-grid-ink">Risk Distribution</h2>
        <div className="mt-5 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={riskData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="risk" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#0f766e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
      <section className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-grid-ink">Consumption Anomaly Trend</h2>
        <div className="mt-5 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data.suspicious_over_time}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="date" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="alerts" fill="#e11d48" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
