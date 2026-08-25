export default function StatusPill({ status }) {
  const tone = status === "Suspicious" || status === "New"
    ? "bg-rose-50 text-rose-700"
    : status === "Under Investigation"
      ? "bg-amber-50 text-amber-700"
      : "bg-emerald-50 text-emerald-700";
  return <span className={`rounded-md px-2.5 py-1 text-xs font-semibold ${tone}`}>{status}</span>;
}
