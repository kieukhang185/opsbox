type Props = {
  label: string;
  value: string | number;
  hint?: string;
  deltaPct?: number;
};
export default function KPICard({ label, value, hint, deltaPct }: Props) {
  const delta =
    typeof deltaPct === "number"
      ? `${deltaPct > 0 ? "▲" : "▼"} ${Math.abs(deltaPct)}%`
      : null;
  return (
    <div className="rounded-xl border border-zinc-300 bg-white p-4 shadow">
      <div className="text-zinc-600 text-sm font-medium">{label}</div>
      <div className="mt-2 text-3xl font-bold text-zinc-900">{value}</div>
      <div className="mt-1 text-xs text-zinc-600 flex gap-2">
        {hint && <span>{hint}</span>}
        {delta && (
          <span
            className={deltaPct! >= 0 ? "text-emerald-700" : "text-rose-700"}
          >
            {delta}
          </span>
        )}
      </div>
    </div>
  );
}
