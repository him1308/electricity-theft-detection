export function formatNumber(value, digits = 0) {
  return new Intl.NumberFormat("en-IN", { maximumFractionDigits: digits }).format(value || 0);
}

export function formatDate(value) {
  if (!value) return "No readings";
  return new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

export function riskTone(level) {
  return {
    Low: "bg-emerald-50 text-emerald-700 border-emerald-200",
    Medium: "bg-amber-50 text-amber-700 border-amber-200",
    High: "bg-orange-50 text-orange-700 border-orange-200",
    Critical: "bg-rose-50 text-rose-700 border-rose-200"
  }[level] || "bg-slate-50 text-slate-700 border-slate-200";
}
