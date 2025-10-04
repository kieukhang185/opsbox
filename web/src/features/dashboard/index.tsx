import KPICard from "@/components/KPICard";
import DataTable from "@/components/DataTable";
import { useQuery } from "@tanstack/react-query";
import { get } from "@/lib/api";
import type { ListResponse, Event } from "@/types";

export default function DashboardPage() {
  const eventsQ = useQuery({
    queryKey: ["events", "warnings"],
    queryFn: () =>
      get<ListResponse<Event>>("/k8s/events", {
        only_warnings: true,
        since_seconds: 900,
        limit: 20,
      }),
  });

  // Placeholder counts: fetch from respective endpoints later
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KPICard label="Namespaces" value="—" hint="Total namespaces" />
        <KPICard label="Nodes" value="—" hint="Ready / Total" />
        <KPICard label="Pods" value="—" hint="By phase" />
        <KPICard
          label="Warnings (15m)"
          value={eventsQ.data?.items.length ?? 0}
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
