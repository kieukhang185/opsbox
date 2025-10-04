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
    <div className="rounded-xl border bg-white p-4 shadow-sm">
      <div className="text-slate-500 text-sm">{label}</div>
      <div className="mt-2 text-3xl font-semibold">{value}</div>
      <div className="mt-1 text-xs text-slate-500 flex gap-2">
        {hint && <span>{hint}</span>}
        {delta && (
          <span
            className={deltaPct! >= 0 ? "text-emerald-600" : "text-rose-600"}
          >
            {delta}
          </span>
        )}
      </div>
    </div>
  );
}
