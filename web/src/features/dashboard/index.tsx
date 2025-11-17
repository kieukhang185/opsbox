import KPICard from "@/components/KPICard";
import DataTable from "@/components/DataTable";
import { useQuery } from "@tanstack/react-query";
import { get, listAllCount, list } from "@/lib/api";
import type { ListResponse, Event, Node, Pod } from "@/types";

export default function DashboardPage() {
  // last 15m warnings
  const eventsQ = useQuery({
    queryKey: ["events", "warnings"],
    queryFn: () =>
      list<Event>("/kubectl/events", {
        only_warnings: true,
        since_seconds: 900,
        limit: 20,
      }),
  });
  console.log("eventsQ:", eventsQ);

  // counts
  const namespacesCountQ = useQuery({
    queryKey: ["namespaces-count"],
    queryFn: () => listAllCount("/kubectl/namespaces", {}),
  });
  console.log("namespacesCountQ:", namespacesCountQ);

  const nodesQ = useQuery({
    queryKey: ["nodes-summary"],
    queryFn: () =>
      list<Node>("/kubectl/nodes", { include_metrics: true, limit: 200 }),
  });

  const podsPhaseQ = useQuery({
    queryKey: ["pods-phase-counts"],
    queryFn: async () => {
      // up to 10 pages x 200
      let token: string | undefined = undefined;
      const counts: Record<string, number> = {};
      for (let i = 0; i < 10; i++) {
        const resp: ListResponse<Pod> = await list<Pod>("/kubectl/pods", {
          limit: 200,
          continue: token,
        });
        for (const p of (resp.items ?? []) as any[]) {
          counts[p.phase] = (counts[p.phase] || 0) + 1;
        }
        token = resp.continue;
        if (!token) break;
      }
      return counts;
    },
  });

  const nodes = nodesQ.data?.items ?? [];
  const ready = nodes.filter((n) => (n as any).ready).length;
  const total = nodes.length;

  const podsCounts = podsPhaseQ.data ?? {};
  const podsTotal = Object.values(podsCounts).reduce(
    (a, b) => a + (b as number),
    0,
  );
  const podsSummary = Object.keys(podsCounts).length
    ? Object.entries(podsCounts)
        .map(([k, v]) => `${k}:${v}`)
        .join(" · ")
    : "—";

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard
          label="Namespaces"
          value={namespacesCountQ.data ?? "—"}
          hint="Total namespaces"
        />
        <KPICard
          label="Nodes"
          value={`${ready}/${total}`}
          hint="Ready / Total"
        />
        <KPICard label="Pods" value={podsTotal || "—"} hint={podsSummary} />
        <KPICard
          label="Warnings (15m)"
          value={eventsQ.data?.items?.length ?? 0}
        />
      </div>

      <section className="space-y-3">
        <h2 className="text-base font-semibold">Recent Warnings</h2>
        <DataTable<Event>
          columns={[
            { key: "last_timestamp", header: "Time" },
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
          rows={eventsQ.data?.items ?? []}
        />
      </section>
    </div>
  );
}
