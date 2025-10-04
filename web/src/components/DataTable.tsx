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
    <div className="overflow-hidden rounded-xl border border-zinc-300 bg-white shadow">
      <table className="min-w-full">
        <thead className="bg-zinc-100">
          <tr className="border-b border-zinc-300">
            {columns.map((c) => (
              <th
                key={String(c.key)}
                className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-zinc-700"
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr
              key={i}
              className="odd:bg-white even:bg-zinc-50 hover:bg-zinc-100 border-b border-zinc-200"
            >
              {columns.map((c) => (
                <td
                  key={String(c.key)}
                  className="px-4 py-2 text-sm text-zinc-900"
                >
                  {c.render ? c.render(r) : String((r as any)[c.key])}
                </td>
              ))}
            </tr>
          ))}
          {!rows.length && (
            <tr>
              <td
                className="px-4 py-8 text-sm text-zinc-600"
                colSpan={columns.length}
              >
                No data.
              </td>
            </tr>
          )}
        </tbody>
      </table>

      {onLoadMore && (
        <div className="p-3 text-center border-t border-zinc-300 bg-zinc-50">
          {hasMore ? (
            <button
              onClick={onLoadMore}
              className="rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm text-zinc-800 hover:bg-zinc-100"
            >
              Load more
            </button>
          ) : (
            <span className="text-xs text-zinc-600">No more rows</span>
          )}
        </div>
      )}
    </div>
  );
}
