import { Upload } from "lucide-react";
import { useState } from "react";

import ErrorState from "../components/ErrorState";
import { api } from "../services/api";

export default function UploadData() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function upload(event) {
    event.preventDefault();
    if (!file) return;
    setLoading(true);
    setError("");
    setResult(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const { data } = await api.post("/data/upload", formData, { headers: { "Content-Type": "multipart/form-data" } });
      setResult(data);
    } catch (err) {
      setError(typeof err.response?.data?.detail === "string" ? err.response.data.detail : "CSV validation failed. Check required columns.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <form onSubmit={upload} className="rounded-lg border border-grid-line bg-white p-6 shadow-panel">
        <h2 className="text-xl font-semibold text-grid-ink">CSV Upload</h2>
        <p className="mt-1 text-sm text-slate-500">Required columns: consumer_id, timestamp, energy_consumption.</p>
        <label className="mt-6 flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-grid-line bg-slate-50 p-10 text-center hover:border-grid-teal">
          <Upload className="text-grid-teal" size={32} />
          <span className="mt-3 font-semibold text-grid-ink">{file ? file.name : "Choose smart meter CSV"}</span>
          <input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0])} className="hidden" />
        </label>
        <button disabled={!file || loading} className="mt-5 rounded-md bg-grid-ink px-4 py-3 font-semibold text-white disabled:opacity-50">
          {loading ? "Processing..." : "Validate and Upload"}
        </button>
      </form>
      {error && <ErrorState message={error} />}
      {result && (
        <section className="rounded-lg border border-grid-line bg-white p-6 shadow-panel">
          <h3 className="text-lg font-semibold text-grid-ink">Upload Result</h3>
          <p className="mt-3 text-sm text-slate-600">{result.inserted_readings} new readings inserted.</p>
          <p className="mt-2 text-sm text-slate-600">{result.predictions.length} consumer predictions generated.</p>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                <tr><th className="p-3">Consumer</th><th className="p-3">Risk</th><th className="p-3">Level</th><th className="p-3">Reasons</th></tr>
              </thead>
              <tbody>
                {result.predictions.slice(0, 10).map((row) => (
                  <tr key={row.consumer_id} className="border-t border-grid-line">
                    <td className="p-3 font-semibold">{row.consumer_id}</td>
                    <td className="p-3">{row.risk_score}</td>
                    <td className="p-3">{row.risk_level}</td>
                    <td className="p-3 text-slate-600">{row.reasons.join("; ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
