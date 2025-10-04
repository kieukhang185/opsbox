import DataTable from "@/components/DataTable";
import { NodeReadyBadge } from "@/components/StatusBadge";
import type { Node } from "@/types";
import { fmtBytes, fmtCpu } from "@/lib/format";
import { useList } from "@/hooks/useList";

export default function NodesPage() {
  const q = useList<Node>("/kubectl/nodes", {
    include_metrics: true,
    limit: 50,
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
        rows={q.items}
        onLoadMore={q.loadMore}
        hasMore={q.hasMore}
      />
    </div>
  );
}
