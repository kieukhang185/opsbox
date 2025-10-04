# K8s Admin (Vite + React + TypeScript + Tailwind)

Read-only admin UI for visualizing Kubernetes metrics via the OpsBox backend.

## Quickstart

```bash
cp .env.example .env
# edit VITE_API_BASE_URL and VITE_API_BASE_WS_URL

npm i
npm run dev
```

## Tech

- Vite + React + TS + Tailwind
- React Router, TanStack Query, Axios
- Simple components: DataTable, KPICard, StatusBadge, LogsViewer
- WS live events stream

## Endpoints used (expected)

- /k8s/namespaces
- /k8s/pods, /k8s/pods/{ns}/{name}, /k8s/pods/{ns}/{name}/logs
- /k8s/nodes?include_metrics=true
- /k8s/events?only_warnings=true&since_seconds=900, WS /k8s/events/stream
