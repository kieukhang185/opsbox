import { useEffect, useRef, useState } from "react";
import { makeWS } from "@/lib/ws";
import { get } from "@/lib/api";
import type { Event } from "@/types";

type ConnState = "connecting" | "live" | "reconnecting" | "paused" | "error";

type Options = {
  /** Append new rows to the head, keep up to maxRows */
  maxRows?: number;
  /** When WS is down, poll this often (ms). Set 0 to disable polling fallback. */
  fallbackPollMs?: number;
  /** Query params for initial/fallback fetches */
  params?: {
    only_warnings?: boolean;
    since_seconds?: number;
    [k: string]: any;
  };
};

function eventKey(e: Event) {
  // Composite key good enough for dedupe
  const o = e.involved_object || ({} as any);
  return `${e.last_timestamp}|${e.reason}|${o.kind}|${o.name}|${
    o.namespace ?? ""
  }`;
}

export function useEventStream(
  path: string,
  { maxRows = 2000, fallbackPollMs = 3000, params = {} }: Options = {},
) {
  const [rows, setRows] = useState<Event[]>([]);
  const [state, setState] = useState<ConnState>("connecting");
  const [paused, setPaused] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<number | null>(null);
  const pollTimer = useRef<number | null>(null);
  const backoffMs = useRef(1000); // start 1s, cap 30s
  const seen = useRef<Set<string>>(new Set());

  // merge helper with dedupe + cap
  const merge = (incoming: Event[]) => {
    if (!incoming?.length) return;
    setRows((prev) => {
      const out = [...incoming, ...prev];
      const deduped: Event[] = [];
      const localSeen = new Set<string>();
      for (const ev of out) {
        const k = eventKey(ev);
        if (!seen.current.has(k) && !localSeen.has(k)) {
          deduped.push(ev);
          localSeen.add(k);
        }
      }
      // update seen set (avoid unbounded growth by trimming)
      for (const k of localSeen) seen.current.add(k);
      if (seen.current.size > maxRows * 2) {
        // trim roughly
        seen.current = new Set(Array.from(seen.current).slice(0, maxRows));
      }
      return deduped.slice(0, maxRows);
    });
  };

  // initial HTTP fetch (useful to fill table fast)
  useEffect(() => {
    let abort = false;
    (async () => {
      try {
        const d = await get<{ items: Event[] }>("/k8s/events", {
          limit: 50,
          ...params,
        });
        if (!abort) merge(d.items || []);
      } catch {}
    })();
    return () => {
      abort = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // fallback polling when disconnected
  const startPolling = () => {
    if (!fallbackPollMs) return;
    stopPolling();
    pollTimer.current = window.setInterval(async () => {
      if (paused) return;
      try {
        const d = await get<{ items: Event[] }>("/k8s/events", {
          limit: 20,
          ...params,
        });
        merge(d.items || []);
      } catch {}
    }, fallbackPollMs);
  };
  const stopPolling = () => {
    if (pollTimer.current) {
      window.clearInterval(pollTimer.current);
      pollTimer.current = null;
    }
  };

  // websocket connect/reconnect
  const connect = () => {
    stopPolling();
    setState(paused ? "paused" : "connecting");
    try {
      const ws = makeWS(path);
      wsRef.current = ws;

      ws.onopen = () => {
        backoffMs.current = 1000;
        if (!paused) setState("live");
        // optional keepalive ping
        const ping = () => {
          try {
            ws.send('{"type":"ping"}');
          } catch {}
        };
        const pingId = window.setInterval(ping, 25000);
        ws.onclose = (ev) => {
          window.clearInterval(pingId);
          if (paused) return; // if user paused, don't auto-reconnect
          scheduleReconnect();
        };
      };

      ws.onmessage = (ev) => {
        if (paused) return;
        try {
          // allow single or batched payloads
          const data = JSON.parse(ev.data);
          const items: Event[] = Array.isArray(data) ? data : [data];
          merge(items);
        } catch {
          // ignore bad frames
        }
      };

      ws.onerror = () => {
        if (paused) return;
        scheduleReconnect();
      };
    } catch {
      scheduleReconnect();
    }
  };

  const scheduleReconnect = () => {
    setState("reconnecting");
    stopPolling();
    // start fallback polling while we wait
    startPolling();
    if (reconnectTimer.current) window.clearTimeout(reconnectTimer.current);
    const jitter = 0.8 + Math.random() * 0.4;
    const delay = Math.min(30000, backoffMs.current) * jitter;
    reconnectTimer.current = window.setTimeout(() => {
      backoffMs.current = Math.min(30000, backoffMs.current * 2);
      connect();
    }, delay) as unknown as number;
  };

  const cleanup = () => {
    if (reconnectTimer.current) window.clearTimeout(reconnectTimer.current);
    reconnectTimer.current = null;
    stopPolling();
    try {
      wsRef.current?.close();
    } catch {}
    wsRef.current = null;
  };

  useEffect(() => {
    if (!paused) connect();
    return cleanup;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paused, path]);

  const pause = () => {
    setPaused(true);
    setState("paused");
    cleanup();
  };
  const resume = () => {
    setPaused(false);
    connect();
  };

  return { rows, state, paused, pause, resume };
}
