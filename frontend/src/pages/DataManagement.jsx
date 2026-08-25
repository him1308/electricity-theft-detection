import { Database, FileText } from "lucide-react";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import StatCard from "../components/StatCard";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { formatDate, formatNumber } from "../utils/format";

export default function DataManagement() {
  const { data, loading, error } = useApi(async () => (await api.get("/admin/data")).data, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2">
        <StatCard icon={Database} label="Total Consumers" value={formatNumber(data.total_consumers)} hint="Consumers currently stored" />
        <StatCard icon={FileText} label="Data Records" value={formatNumber(data.total_readings)} hint="Consumption readings in the database" tone="text-indigo-700" />
      </section>

      <section className="rounded-lg border border-grid-line bg-white shadow-panel">
        <div className="border-b border-grid-line p-5">
          <h2 className="text-xl font-semibold text-grid-ink">Uploaded Datasets</h2>
          <p className="mt-1 text-sm text-slate-500">Stored CSV files from the backend uploads directory.</p>
        </div>
        {data.uploaded_datasets.length === 0 ? (
          <div className="p-6 text-sm text-slate-500">No uploaded CSV files found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[760px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-3">Dataset</th>
                  <th className="px-5 py-3">Records</th>
                  <th className="px-5 py-3">Size</th>
                  <th className="px-5 py-3">Uploaded</th>
                  <th className="px-5 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-grid-line">
                {data.uploaded_datasets.map((dataset) => (
                  <tr key={dataset.filename} className="hover:bg-slate-50">
                    <td className="px-5 py-4 font-semibold text-grid-ink">{dataset.filename}</td>
                    <td className="px-5 py-4">{dataset.records == null ? "-" : formatNumber(dataset.records)}</td>
                    <td className="px-5 py-4">{formatBytes(dataset.size_bytes)}</td>
                    <td className="px-5 py-4 text-slate-500">{formatDate(dataset.uploaded_at)}</td>
                    <td className="px-5 py-4">
                      <span className="rounded-md bg-emerald-50 px-3 py-2 font-semibold text-emerald-700">{dataset.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <p className="rounded-lg border border-grid-line bg-white p-5 text-sm text-slate-600 shadow-panel">
        Dataset deletion and database reset are intentionally not exposed because uploaded files are not linked to ingested readings by dataset lineage in the current data model.
      </p>
    </div>
  );
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${formatNumber(bytes / 1024, 1)} KB`;
  return `${formatNumber(bytes / (1024 * 1024), 1)} MB`;
}
