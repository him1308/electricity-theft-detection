import { Activity, AlertOctagon, ClipboardList, Database, Gauge, ShieldCheck, UploadCloud, UserCheck, Users, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import RiskBadge from "../components/RiskBadge";
import StatCard from "../components/StatCard";
import { api } from "../services/api";
import { formatDate, formatNumber } from "../utils/format";
import { useApi } from "../hooks/useApi";

const colors = ["#10b981", "#f59e0b", "#f97316", "#e11d48"];

export default function Dashboard() {
  const role = localStorage.getItem("role") || "Analyst";
  const isAdmin = role.toLowerCase() === "admin";
  const { data, loading, error } = useApi(
    async () => {
      const [summary, roleSummary] = await Promise.all([
        api.get("/dashboard/summary"),
        api.get(isAdmin ? "/dashboard/admin" : "/dashboard/analyst")
      ]);
      return { summary: summary.data, roleSummary: roleSummary.data };
    },
    [isAdmin]
  );

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return isAdmin ? <AdminDashboard data={data} /> : <AnalystDashboard data={data} />;
}

function AdminDashboard({ data }) {
  const riskData = Object.entries(data.summary.risk_distribution).map(([name, value]) => ({ name, value }));
  const performance = data.roleSummary.model_performance;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard icon={Users} label="Total Consumers" value={formatNumber(data.roleSummary.total_consumers)} hint="Registered smart meter accounts" />
        <StatCard icon={AlertOctagon} label="High Risk Consumers" value={formatNumber(data.roleSummary.high_risk_consumers)} hint="High and critical open alerts" tone="text-rose-700" />
        <StatCard icon={ShieldCheck} label="Active Alerts" value={formatNumber(data.roleSummary.active_alerts)} hint="Alerts not dismissed" tone="text-orange-700" />
        <StatCard icon={UserCheck} label="Total Analysts" value={formatNumber(data.roleSummary.total_analysts)} hint="Users assigned analyst access" tone="text-indigo-700" />
        <StatCard icon={Users} label="Total Users" value={formatNumber(data.roleSummary.total_users)} hint="All authenticated accounts" />
        <StatCard icon={Database} label="Data Records" value={formatNumber(data.roleSummary.data_records)} hint="Stored meter readings" tone="text-indigo-700" />
        <StatCard icon={Gauge} label="Model Performance" value={performance == null ? "-" : `${formatNumber(performance <= 1 ? performance * 100 : performance, 1)}%`} hint="Latest F1, accuracy, or ROC AUC" tone="text-amber-700" />
        <StatCard icon={UploadCloud} label="Latest Data Upload" value={formatDate(data.roleSummary.latest_data_upload)} hint="Newest stored CSV upload" />
        <StatCard icon={Zap} label="Avg Consumption" value={`${formatNumber(data.summary.average_consumption, 1)} kWh`} hint="Across uploaded readings" />
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel xl:col-span-2">
          <h2 className="text-lg font-semibold text-grid-ink">Daily Energy Consumption</h2>
          <div className="mt-5 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.summary.daily_consumption}>
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
            <BarChart data={data.summary.suspicious_over_time}>
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

function AnalystDashboard({ data }) {
  const riskData = Object.entries(data.summary.risk_distribution).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard icon={ClipboardList} label="Consumers Analyzed" value={formatNumber(data.roleSummary.consumers_analyzed)} hint="Consumers with readings in the system" />
        <StatCard icon={AlertOctagon} label="High Risk Consumers" value={formatNumber(data.roleSummary.high_risk_consumers)} hint="Needs immediate investigation" tone="text-rose-700" />
        <StatCard icon={Activity} label="Medium Risk Consumers" value={formatNumber(data.roleSummary.medium_risk_consumers)} hint="Watchlist candidates" tone="text-amber-700" />
        <StatCard icon={ShieldCheck} label="Pending Investigations" value={formatNumber(data.roleSummary.pending_investigations)} hint="New or under investigation alerts" tone="text-orange-700" />
        <StatCard icon={AlertOctagon} label="Active Alerts" value={formatNumber(data.roleSummary.active_alerts)} hint="Alerts not dismissed" tone="text-rose-700" />
        <StatCard icon={Gauge} label="Avg Risk Score" value={formatNumber(data.summary.average_risk_score, 1)} hint="Average across alert history" />
      </section>

      <section className="rounded-lg border border-grid-line bg-white shadow-panel">
        <div className="border-b border-grid-line p-5">
          <h2 className="text-lg font-semibold text-grid-ink">Recent Suspicious Consumers</h2>
          <p className="mt-1 text-sm text-slate-500">Open high and critical risk consumers requiring attention.</p>
        </div>
        {data.roleSummary.recent_suspicious_consumers.length === 0 ? (
          <div className="p-6 text-sm text-slate-500">No high-risk open investigations found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-3">Consumer</th>
                  <th className="px-5 py-3">Location</th>
                  <th className="px-5 py-3">Risk</th>
                  <th className="px-5 py-3">Average</th>
                  <th className="px-5 py-3">Last Reading</th>
                  <th className="px-5 py-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-grid-line">
                {data.roleSummary.recent_suspicious_consumers.map((consumer) => (
                  <tr key={consumer.consumer_id} className="hover:bg-slate-50">
                    <td className="px-5 py-4 font-semibold text-grid-ink">{consumer.consumer_id}</td>
                    <td className="px-5 py-4">{consumer.location}</td>
                    <td className="px-5 py-4"><RiskBadge level={consumer.risk_level} /></td>
                    <td className="px-5 py-4">{formatNumber(consumer.average_consumption, 2)} kWh</td>
                    <td className="px-5 py-4 text-slate-500">{formatDate(consumer.last_reading)}</td>
                    <td className="px-5 py-4">
                      <Link to={`/consumers/${consumer.consumer_id}`} className="rounded-md bg-grid-ink px-3 py-2 text-xs font-semibold text-white">Investigate</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-grid-ink">Risk Distribution</h2>
          <div className="mt-5 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" outerRadius={96} label>
                  {riskData.map((entry, index) => <Cell key={entry.name} fill={colors[index % colors.length]} />)}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
          <h2 className="text-lg font-semibold text-grid-ink">Suspicious Consumers Over Time</h2>
          <div className="mt-5 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.summary.suspicious_over_time}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="alerts" fill="#e11d48" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
}
