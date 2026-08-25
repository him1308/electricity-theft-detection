import { Settings } from "lucide-react";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { formatNumber } from "../utils/format";

export default function SystemSettings() {
  const { data, loading, error } = useApi(async () => (await api.get("/admin/settings")).data, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const rows = [
    ["Application", data.app_name],
    ["API Prefix", data.api_prefix],
    ["Token Expiry", `${formatNumber(data.access_token_expire_minutes)} minutes`],
    ["Database Backend", data.database_backend],
    ["Model Path", data.model_path],
    ["Uploads Directory", data.uploads_directory],
    ["CORS Origins", data.cors_origins.join(", ") || "-"],
    ["Configuration Source", data.configuration_source]
  ];

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-grid-line bg-white p-6 shadow-panel">
        <div className="flex items-start gap-4">
          <div className="grid h-12 w-12 place-items-center rounded-lg bg-slate-100 text-grid-teal">
            <Settings size={24} />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-grid-ink">System Settings</h2>
            <p className="mt-1 text-sm text-slate-500">Runtime configuration currently managed by backend settings and environment variables.</p>
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-grid-line bg-white shadow-panel">
        <div className="divide-y divide-grid-line">
          {rows.map(([label, value]) => (
            <div key={label} className="grid gap-2 p-5 md:grid-cols-[220px_1fr]">
              <p className="text-sm font-semibold text-slate-500">{label}</p>
              <p className="break-words text-sm font-medium text-grid-ink">{value}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
