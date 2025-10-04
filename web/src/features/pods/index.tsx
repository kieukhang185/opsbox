import DataTable from "@/components/DataTable";
import { PodPhaseBadge } from "@/components/StatusBadge";
import type { Pod } from "@/types";
import { useList } from "@/hooks/useList";

export default function PodsPage() {
  const q = useList<Pod>("/kubectl/pods", { limit: 50 });

  return (
    <div className="space-y-3">
      <h2 className="text-base font-semibold">Pods</h2>
      <DataTable<Pod>
        columns={[
          { key: "namespace", header: "Namespace" },
          { key: "name", header: "Name" },
          {
            key: "phase",
            header: "Phase",
            render: (p) => <PodPhaseBadge phase={p.phase} />,
          },
          { key: "node", header: "Node" },
          { key: "start_time", header: "Start" },
        ]}
        rows={q.items}
        onLoadMore={q.loadMore}
        hasMore={q.hasMore}
      />
    </div>
  );
}
