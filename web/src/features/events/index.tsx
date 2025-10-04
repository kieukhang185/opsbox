import DataTable from "@/components/DataTable";
import { useEffect, useRef, useState } from "react";
import { get } from "@/lib/api";
import { makeWS } from "@/lib/ws";
import type { Event, ListResponse } from "@/types";

export default function EventsPage() {
  const [rows, setRows] = useState<Event[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // initial load (warnings last 15 min)
    get<ListResponse<Event>>("/kubectl/events", {
      only_warnings: true,
      since_seconds: 900,
    })
      .then((d) => setRows(d.items ?? []))
      .catch(() => {});

    // live stream
    const ws = makeWS("/kubectl/events/stream");
    wsRef.current = ws;
    ws.onmessage = (ev) => {
      try {
        const e: Event = JSON.parse(ev.data);
        setRows((prev) => [e, ...prev].slice(0, 2000));
      } catch {}
    };
    ws.onclose = () => {
      // basic reconnect
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    };
    return () => {
      ws.close();
    };
  }, []);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold">Events (live)</h2>
        <span className="text-xs text-slate-500">Streaming…</span>
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
