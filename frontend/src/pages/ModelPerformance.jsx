import { Brain, Play } from "lucide-react";
import { useState } from "react";

import ErrorState from "../components/ErrorState";
import LoadingState from "../components/LoadingState";
import { useApi } from "../hooks/useApi";
import { api } from "../services/api";
import { formatDate, formatNumber } from "../utils/format";

export default function ModelPerformance() {
  const [refresh, setRefresh] = useState(0);
  const [training, setTraining] = useState(false);
  const { data, loading, error } = useApi(async () => (await api.get("/model/status")).data, [refresh]);
  const [trainError, setTrainError] = useState("");
  const isAdmin = (localStorage.getItem("role") || "").toLowerCase() === "admin";

  async function train() {
    setTraining(true);
    setTrainError("");
    try {
      await api.post("/model/train");
      setRefresh((value) => value + 1);
    } catch (err) {
      setTrainError(err.response?.data?.detail || err.message);
    } finally {
      setTraining(false);
    }
  }

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-grid-line bg-white p-6 shadow-panel">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="flex gap-4">
            <div className="grid h-12 w-12 place-items-center rounded-lg bg-slate-100 text-grid-teal">
              <Brain size={24} />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-grid-ink">{data.model_name || "No trained model"}</h2>
              <p className="mt-1 text-sm text-slate-500">Model status: {data.is_trained ? "Trained and persisted" : "Training required"}</p>
            </div>
          </div>
          {isAdmin && (
            <button onClick={train} disabled={training} className="flex items-center justify-center gap-2 rounded-md bg-grid-ink px-4 py-3 font-semibold text-white disabled:opacity-60">
              <Play size={18} />
              {training ? "Training..." : "Train Model"}
            </button>
          )}
        </div>
        {trainError && <ErrorState message={trainError} />}
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric label="Version" value={data.version || "-"} />
        <Metric label="Training Date" value={data.trained_at ? formatDate(data.trained_at) : "-"} />
        <Metric label="Samples" value={formatNumber(data.samples)} />
        <Metric label="Features" value={formatNumber(data.features)} />
      </section>
      <p className="rounded-lg border border-grid-line bg-white p-5 text-sm text-slate-600 shadow-panel">
        The default workflow uses Isolation Forest when reliable theft labels are unavailable. If labeled data includes is_theft, theft_label, fraud_label, or label, the backend switches to a supervised Random Forest with a Logistic Regression baseline.
      </p>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-lg border border-grid-line bg-white p-5 shadow-panel">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-lg font-semibold text-grid-ink">{value}</p>
    </div>
  );
}
