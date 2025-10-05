export function makeWS(path: string): WebSocket {
  const base = import.meta.env.VITE_API_BASE_WS_URL || "";
  const url = base.replace(/\/$/, "") + path;
  return new WebSocket(url);
}
