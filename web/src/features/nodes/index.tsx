import DataTable from "@/components/DataTable";
import { NodeReadyBadge } from "@/components/StatusBadge";
import { useQuery } from "@tanstack/react-query";
import { get } from "@/lib/api";
import type { ListResponse, Node } from "@/types";
import { fmtBytes, fmtCpu } from "@/lib/format";

export default function NodesPage() {
  const q = useQuery({
    queryKey: ["nodes"],
    queryFn: () =>
      get<ListResponse<Node>>("/k8s/nodes", { include_metrics: true }),
  });

  return (
    <div className="space-y-3">
      <h2 className="text-base font-semibold">Nodes</h2>
      <DataTable<Node>
        columns={[
          { key: "name", header: "Name" },
          {
            key: "ready",
            header: "Ready",
            render: (n) => <NodeReadyBadge ready={n.ready} />,
          },
          {
            key: "allocatable",
            header: "Allocatable",
            render: (n) =>
              `${fmtCpu(n.allocatable.cpu)} / ${fmtBytes(
                n.allocatable.memory,
              )}`,
          },
          {
            key: "usage",
            header: "Usage",
            render: (n) =>
              n.usage
                ? `${fmtCpu(n.usage.cpu)} / ${fmtBytes(n.usage.memory)}`
                : "—",
          },
          {
            key: "addresses",
            header: "Internal IP",
            render: (n) => n.addresses?.internal || "—",
          },
        ]}
        rows={q.data?.items ?? []}
      />
    </div>
  );
}
