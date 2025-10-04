export const fmtInt = (n: number | undefined) => (n ?? 0).toLocaleString();
export const fmtBytes = (b?: number | string) => {
  const n = typeof b === "string" ? parseFloat(b) : b ?? 0;
  if (n < 1024) return `${n} B`;
  const units = ["KiB", "MiB", "GiB", "TiB"];
  let i = -1,
    v = n;
  do {
    v /= 1024;
    i++;
  } while (v >= 1024 && i < units.length - 1);
  return `${v.toFixed(1)} ${units[i]}`;
};
export const fmtCpu = (m?: number | string) => {
  const n = typeof m === "string" ? parseFloat(m) : m ?? 0;
  return n >= 1000 ? `${(n / 1000).toFixed(2)} cores` : `${n} m`;
};
