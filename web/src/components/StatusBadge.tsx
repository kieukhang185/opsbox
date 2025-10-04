export function PodPhaseBadge({ phase }: { phase: string }) {
  const cls =
    phase === "Running"
      ? "bg-emerald-100 text-emerald-700"
      : phase === "Pending"
        ? "bg-amber-100 text-amber-700"
        : phase === "Failed"
          ? "bg-rose-100 text-rose-700"
          : "bg-slate-100 text-slate-700";
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${cls}`}
    >
      {phase}
    </span>
  );
}

export function NodeReadyBadge({ ready }: { ready: boolean }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
        ready ? "bg-emerald-100 text-emerald-700" : "bg-rose-100 text-rose-700"
      }`}
    >
      {ready ? "Ready" : "Not Ready"}
    </span>
  );
}
