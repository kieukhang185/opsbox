import DataTable from "@/components/DataTable";
import type { Namespace } from "@/types";
import { useList } from "@/hooks/useList";

export default function NamespacesPage() {
  const q = useList<Namespace>("/kubectl/namespaces", { limit: 50 });

  return (
    <div className="space-y-3">
      <h2 className="text-base font-semibold">Namespaces</h2>
      <DataTable<Namespace>
        columns={[
          { key: "name", header: "Name" },
          { key: "status", header: "Status" },
          { key: "creation_timestamp", header: "Created" },
        ]}
        rows={q.items}
        onLoadMore={q.loadMore}
        hasMore={q.hasMore}
      />
    </div>
  );
}
