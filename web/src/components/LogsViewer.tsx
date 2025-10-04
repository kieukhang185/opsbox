import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

type Props = {
  namespace: string;
  name: string;
  tailLines?: number;
  intervalMs?: number;
};

export default function LogsViewer({
  namespace,
  name,
  tailLines = 1000,
  intervalMs = 2000,
}: Props) {
  const [text, setText] = useState<string>("");
  const [paused, setPaused] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let timer: number | undefined;
    const fetchLogs = async () => {
      try {
        const res = await api.get<string>(
          `/kubectl/pods/${namespace}/${name}/logs`,
          { params: { tail_lines: tailLines } },
        );
        setText(res.data);
        if (ref.current && !paused)
          ref.current.scrollTop = ref.current.scrollHeight;
      } catch (e) {
        // ignore for now
      }
    };
    fetchLogs();
    timer = window.setInterval(() => {
      if (!paused) fetchLogs();
    }, intervalMs);
    return () => {
      if (timer) window.clearInterval(timer);
    };
  }, [namespace, name, tailLines, intervalMs, paused]);

  return (
    <div className="rounded-xl border bg-white">
      <div className="flex items-center justify-between border-b px-3 py-2">
        <div className="text-sm font-medium">Logs</div>
        <button
          onClick={() => setPaused((p) => !p)}
          className="text-xs rounded border px-2 py-1 hover:bg-slate-50"
        >
          {paused ? "Resume" : "Pause"}
        </button>
      </div>
      <div
        ref={ref}
        className="h-80 overflow-auto p-3 font-mono text-xs whitespace-pre-wrap"
      >
        {text || "No logs."}
      </div>
    </div>
  );
}
