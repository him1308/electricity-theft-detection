import { AlertTriangle, Gauge } from "lucide-react";
import { useParams } from "react-router-dom";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import RiskBadge from "../components/RiskBadge";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { formatDate, formatNumber } from "../utils/format";

export default function ConsumerDetails() {
  const { consumerId } = useParams();
  const { data, loading, error } = useApi(
    async () => {
      const [consumer, readings] = await Promise.all([
        api.get(`/consumers/${consumerId}`),
        api.get(`/consumers/${consumerId}/consumption`)
      ]);
      return { consumer: consumer.data, readings: readings.data };
    },
    [consumerId]
  );

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const chartData = data.readings.map((item) => ({
    date: new Date(item.timestamp).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
    consumption: item.energy_consumption
  }));

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-grid-line bg-white p-6 shadow-panel">
        <div className="flex flex-col gap-5 md:flex-row md:items-start md:justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-grid-ink">{data.consumer.consumer_id}</h2>
            <p className="mt-1 text-sm text-slate-500">{data.consumer.location} | Meter {data.consumer.meter_number}</p>
            <p className="mt-1 text-sm text-slate-500">Last reading: {formatDate(data.consumer.last_reading)}</p>
          </div>
          <div className="flex items-center gap-3">
            <RiskBadge level={data.consumer.risk_level} />
            <div className="rounded-md bg-slate-100 px-3 py-2 font-semibold text-grid-ink">Score {data.consumer.risk_score}</div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel xl:col-span-2">
          <h3 className="text-lg font-semibold text-grid-ink">Historical Consumption</h3>
          <div className="mt-5 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" minTickGap={24} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="consumption" stroke="#0f766e" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
          <h3 className="text-lg font-semibold text-grid-ink">ML Analysis</h3>
          <div className="mt-5 space-y-4">
            <div className="flex items-center justify-between rounded-md bg-slate-50 p-4">
              <span className="flex items-center gap-2 font-semibold text-slate-700"><Gauge size={18} /> Average</span>
              <span className="font-bold text-grid-ink">{formatNumber(data.consumer.average_consumption, 2)} kWh</span>
            </div>
            <div className="rounded-md bg-amber-50 p-4 text-sm text-amber-800">
              <div className="mb-2 flex items-center gap-2 font-bold"><AlertTriangle size={18} /> Suspicious Indicators</div>
              <p>Open alert reasons are shown on the Alerts page. Predictions describe suspicious/anomalous consumption only and require field verification.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
