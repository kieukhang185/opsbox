import { useQuery } from "@tanstack/react-query";
import { list, ListParams } from "@/lib/api";
import { useState } from "react";

export function useList<T>(
  path: string,
  params?: Omit<ListParams, "continue">,
) {
  const [token, setToken] = useState<string | undefined>(undefined);

  const q = useQuery({
    queryKey: [path, params, token],
    queryFn: () => list<T>(path, { ...params, continue: token }),
    refetchOnMount: true,
  });

  const items = q.data?.items ?? [];
  const hasMore = Boolean(q.data?.continue);
  const loadMore = () => setToken(q.data?.continue);
  const reset = () => setToken(undefined);

  return { ...q, items, hasMore, loadMore, reset };
}
