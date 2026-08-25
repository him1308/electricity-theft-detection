import { AlertOctagon, Activity, Gauge, Users, Zap, Database } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import StatCard from "../components/StatCard";
import { api } from "../services/api";
import { formatNumber } from "../utils/format";
import { useApi } from "../hooks/useApi";

const colors = ["#10b981", "#f59e0b", "#f97316", "#e11d48"];

export default function Dashboard() {
  const { data, loading, error } = useApi(async () => (await api.get("/dashboard/summary")).data, []);
  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const riskData = Object.entries(data.risk_distribution).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard icon={Users} label="Total Consumers" value={formatNumber(data.total_consumers)} hint="Registered smart meter accounts" />
        <StatCard icon={Database} label="Meter Readings" value={formatNumber(data.total_readings)} hint="Validated consumption records" tone="text-indigo-700" />
        <StatCard icon={AlertOctagon} label="Suspicious Consumers" value={formatNumber(data.suspicious_consumers)} hint="Open anomaly investigations" tone="text-rose-700" />
        <StatCard icon={Gauge} label="Critical Alerts" value={formatNumber(data.critical_alerts)} hint="Highest priority inspection queue" tone="text-orange-700" />
        <StatCard icon={Zap} label="Avg Consumption" value={`${formatNumber(data.average_consumption, 1)} kWh`} hint="Across uploaded readings" />
        <StatCard icon={Activity} label="Avg Risk Score" value={formatNumber(data.average_risk_score, 1)} hint="Open alert average" tone="text-amber-700" />
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel xl:col-span-2">
          <h2 className="text-lg font-semibold text-grid-ink">Daily Energy Consumption</h2>
          <div className="mt-5 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.daily_consumption}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" minTickGap={28} />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="consumption" stroke="#0f766e" fill="#ccfbf1" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-grid-ink">Risk Distribution</h2>
          <div className="mt-5 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" outerRadius={105} label>
                  {riskData.map((entry, index) => <Cell key={entry.name} fill={colors[index % colors.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
        <h2 className="text-lg font-semibold text-grid-ink">Suspicious Consumers Over Time</h2>
        <div className="mt-5 h-72">
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
