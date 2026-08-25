import { Search } from "lucide-react";
import { Link } from "react-router-dom";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import RiskBadge from "../components/RiskBadge";
import StatusPill from "../components/StatusPill";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { formatDate, formatNumber } from "../utils/format";

export default function Consumers() {
  const { data, loading, error, setData } = useApi(async () => (await api.get("/consumers")).data, []);

  async function search(event) {
    const query = event.target.value;
    const { data: rows } = await api.get("/consumers", { params: { search: query || undefined } });
    setData(rows);
  }

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="rounded-lg border border-grid-line bg-white shadow-panel">
      <div className="flex flex-col gap-4 border-b border-grid-line p-5 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-grid-ink">Consumer Monitoring</h2>
          <p className="text-sm text-slate-500">Search and review consumer risk profiles.</p>
        </div>
        <div className="flex items-center gap-2 rounded-md border border-grid-line px-3 py-2">
          <Search size={18} className="text-slate-400" />
          <input onChange={search} placeholder="Search consumer" className="w-56 outline-none" />
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="px-5 py-3">Consumer ID</th>
              <th className="px-5 py-3">Location</th>
              <th className="px-5 py-3">Average Consumption</th>
              <th className="px-5 py-3">Risk Score</th>
              <th className="px-5 py-3">Risk Level</th>
              <th className="px-5 py-3">Status</th>
              <th className="px-5 py-3">Last Reading</th>
              <th className="px-5 py-3">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-grid-line">
            {data.map((consumer) => (
              <tr key={consumer.consumer_id} className="hover:bg-slate-50">
                <td className="px-5 py-4 font-semibold text-grid-ink">{consumer.consumer_id}</td>
                <td className="px-5 py-4">{consumer.location}</td>
                <td className="px-5 py-4">{formatNumber(consumer.average_consumption, 2)} kWh</td>
                <td className="px-5 py-4 font-semibold">{consumer.risk_score}</td>
                <td className="px-5 py-4"><RiskBadge level={consumer.risk_level} /></td>
                <td className="px-5 py-4"><StatusPill status={consumer.status} /></td>
                <td className="px-5 py-4 text-slate-500">{formatDate(consumer.last_reading)}</td>
                <td className="px-5 py-4">
                  <Link to={`/consumers/${consumer.consumer_id}`} className="rounded-md bg-grid-ink px-3 py-2 text-xs font-semibold text-white">View</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
