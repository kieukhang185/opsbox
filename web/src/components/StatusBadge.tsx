export function PodPhaseBadge({ phase }: { phase: string }) {
  const cls =
    phase === "Running"
      ? "bg-emerald-100 text-emerald-800 border-emerald-300"
      : phase === "Pending"
        ? "bg-amber-100 text-amber-800 border-amber-300"
        : phase === "Failed"
          ? "bg-rose-100 text-rose-800 border-rose-300"
          : "bg-zinc-100 text-zinc-800 border-zinc-300";
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold ${cls}`}
    >
      {phase}
    </span>
  );
}

export function NodeReadyBadge({ ready }: { ready: boolean }) {
  const cls = ready
    ? "bg-emerald-100 text-emerald-800 border-emerald-300"
    : "bg-rose-100 text-rose-800 border-rose-300";
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold ${cls}`}
    >
      {ready ? "Ready" : "Not Ready"}
    </span>
  );
}
