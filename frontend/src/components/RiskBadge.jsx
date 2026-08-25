import { riskTone } from "../utils/format";

export default function RiskBadge({ level }) {
  return (
    <span className={`inline-flex min-w-20 items-center justify-center rounded-md border px-2.5 py-1 text-xs font-semibold ${riskTone(level)}`}>
      {level}
    </span>
  );
}
