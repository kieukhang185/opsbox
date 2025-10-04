import { ReactNode } from "react";

type Column<T> = {
  key: keyof T | string;
  header: string;
  render?: (row: T) => ReactNode;
};
type Props<T> = {
  columns: Column<T>[];
  rows: T[];
  onLoadMore?: () => void;
  hasMore?: boolean;
};

export default function DataTable<T>({
  columns,
  rows,
  onLoadMore,
  hasMore,
}: Props<T>) {
  return (
    <div className="overflow-hidden rounded-xl border bg-white">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((c) => (
              <th
                key={String(c.key)}
                className="px-4 py-2 text-left text-xs font-medium text-slate-600 uppercase tracking-wider"
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((r, i) => (
            <tr key={i} className="hover:bg-slate-50">
              {columns.map((c) => (
                <td
                  key={String(c.key)}
                  className="px-4 py-2 text-sm text-slate-800"
                >
                  {c.render ? c.render(r) : String((r as any)[c.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {onLoadMore && (
        <div className="p-3 text-center">
          {hasMore ? (
            <button
              onClick={onLoadMore}
              className="rounded-lg border px-3 py-1.5 text-sm hover:bg-slate-50"
            >
              Load more
            </button>
          ) : (
            <span className="text-xs text-slate-500">No more rows</span>
          )}
        </div>
      )}
    </div>
  );
}
