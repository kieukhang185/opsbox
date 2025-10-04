import DataTable from "@/components/DataTable";
import { useQuery } from "@tanstack/react-query";
import { get } from "@/lib/api";
import type { ListResponse, Namespace } from "@/types";

export default function NamespacesPage() {
  const q = useQuery({
    queryKey: ["namespaces"],
    queryFn: () => get<ListResponse<Namespace>>("/k8s/namespaces"),
  });

  return (
    <div className="space-y-3">
      <h2 className="text-base font-semibold">Namespaces</h2>
      <DataTable<Namespace>
        columns={[
          { key: "name", header: "Name" },
          { key: "status", header: "Status" },
          { key: "creation_timestamp", header: "Created" },
        ]}
        rows={q.data?.items ?? []}
      />
    </div>
  );
}
