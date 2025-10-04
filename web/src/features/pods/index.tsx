import DataTable from "@/components/DataTable";
import { PodPhaseBadge } from "@/components/StatusBadge";
import { useQuery } from "@tanstack/react-query";
import { get } from "@/lib/api";
import type { ListResponse, Pod } from "@/types";

export default function PodsPage() {
  const q = useQuery({
    queryKey: ["pods"],
    queryFn: () => get<ListResponse<Pod>>("/k8s/pods"),
  });

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
        rows={q.data?.items ?? []}
      />
    </div>
  );
}
