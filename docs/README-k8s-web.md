# OpsBox K8s Web Console (Vite)

This document describes a new Vite-based frontend to visualize Kubernetes resources and metrics in near real-time.

## Goals
- Provide a simple, read-only web console for OpsBox clusters.
- Show workloads, pods, events, logs, and metrics with live updates.

## Architecture
- **Frontend**: Vite + React + TypeScript, Tailwind, shadcn/ui, React Query, Recharts.
- **Backend**: Extend the existing FastAPI API with `/k8s/*` and `/watch/*` routes.
  - Proxies K8s list/watch APIs, Prometheus queries, and Loki logs.
  - Provides SSE endpoints for near real-time updates.

## Pages
- **Overview**: Cluster tiles, alerts, top pods.
- **Workloads**: Deployments, Jobs, with drill-down.
- **Pods**: Virtualized table, filters, details (logs, metrics, events).
- **Events**: Live stream via SSE.
- **Secrets**: Metadata only (name, type, age).

## Data Strategy
- SSE for watchable resources (pods, events).
- Poll Prometheus (CPU/Mem) every 5–10s.
- Loki logs proxy with safe defaults (5m window, 10k lines).

## Security
- Read-only ServiceAccount scoped to dev namespace (configurable).
- Secrets endpoints return metadata only.
- Rate limits and query guardrails in backend.

## CI/CD
- Reuse OpsBox pipeline: lint, test, build, scan, sign, Helm deploy.
- Playwright e2e tests for live UI.
- K6 perf checks on backend endpoints.

## Acceptance
- Pods scale reflected in UI < 5s.
- Pod detail shows CPU/Mem charts with ≤10s refresh.
- Event stream updates within 2s.
- Logs tail with pause/resume.

---
