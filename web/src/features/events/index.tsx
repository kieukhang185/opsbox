import DataTable from "@/components/DataTable";
import { useEventStream } from "@/hooks/useEventStream";
import type { Event } from "@/types";

export default function EventsPage() {
  // Live stream + HTTP fallback; last 15m warnings as your default filter
  const { rows, state, paused, pause, resume } = useEventStream(
    "/kubectl/events/stream",
    {
      maxRows: 2000,
      fallbackPollMs: 3000,
      params: { only_warnings: true, since_seconds: 900 },
    },
  );

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Events</h2>
        <div className="flex items-center gap-2">
          <span
            className={
              "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold border " +
              (state === "live"
                ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                : state === "reconnecting"
                  ? "bg-amber-100 text-amber-800 border-amber-300"
                  : state === "paused"
                    ? "bg-zinc-100 text-zinc-800 border-zinc-300"
                    : "bg-rose-100 text-rose-800 border-rose-300")
            }
            title="Connection status"
          >
            {state}
          </span>
          {paused ? (
            <button
              onClick={resume}
              className="text-xs rounded-md border border-zinc-300 bg-white px-2 py-1 text-zinc-800 hover:bg-zinc-100"
            >
              Resume
            </button>
          ) : (
            <button
              onClick={pause}
              className="text-xs rounded-md border border-zinc-300 bg-white px-2 py-1 text-zinc-800 hover:bg-zinc-100"
            >
              Pause
            </button>
          )}
        </div>
      </div>

      <DataTable<Event>
        columns={[
          { key: "last_timestamp", header: "Time" },
          { key: "type", header: "Type" },
          { key: "reason", header: "Reason" },
          { key: "message", header: "Message" },
          {
            key: "involved_object",
            header: "Object",
            render: (e) =>
              `${e.involved_object.kind}/${e.involved_object.name}${
                e.involved_object.namespace
                  ? " (" + e.involved_object.namespace + ")"
                  : ""
              }`,
          },
        ]}
        rows={rows}
      />
    </div>
  );
}
