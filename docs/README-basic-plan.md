# OpsBox — Basic plan

1. **Epic: E0 – Repo Bootstrap & Tooling**
Tasks (1pt each):
- Init repo & base folders (api/, worker/, ops/scripts/, ops/helm/, tools/opsbox_cli/) (1pt).
- Add Makefile targets: build, test, run, fmt, lint, pipeline-local (1pt).
- Pre-commit with ruff/black/isort + shellcheck (1pt).
- .dockerignore baseline (1pt).

Subtasks (use for each 1-pt task):
- Implement
- Tests (if applicable)
- Docs/README note
- CI lint/format passes

2. **Epic: E1 – Python API (FastAPI)**
Tasks (1pt each):
- E1-S1: /health returns {status:"ok"}; ≤100ms locally. (1pt)
- E1-S2: CRUD /tasks (id, title, status, created_at, result) + integration tests. (1pt)
- E1-S3: /tasks/{id}/run enqueues background job; status DONE/FAILED. (1pt)
- E1-S4: /metrics with Prometheus (http server + custom counters). (1pt)
- E1-S5: OpenTelemetry tracing to OTLP; spans visible. (1pt)

Subtasks (for each task above):
- Code
- Unit/integration tests
- Verify acceptance criteria
- Update API docs/README
- Expose metrics as needed

3. **Epic: E2 – Python Worker**
Tasks (1pt each):
- E2-S1: Consume job; simulate CPU/IO; persist result. (1pt)
- E2-S2: Hourly cleanup with APScheduler; configurable retention. (1pt)
- E2-S3: Graceful shutdown, retries (3x), dead-letter simulation. (1pt)
- Subtasks: implement, logs for evidence, tests, metrics/logs wired.

4. **Epic: E3 – Data (Postgres) & Migrations**
Tasks (1pt each):
- E3-S1: Define schema + Alembic migrations; alembic upgrade head OK. (1pt)
- E3-S2: Connection pool & health checks; API fast-fails if DB down. (1pt)

5. **Epic: E4 – Queue (Redis)**
Tasks (1pt each):
- E4-S1: Provision Redis via Helm; worker connects; metrics exported. (1pt)

6. **Epic: E5 – Containerization**
Tasks (1pt each):
- E5-S1: Multi-stage Dockerfiles (api/worker) with non-root user, <200MB. (1pt)
- E5-S2: Add healthcheck commands; docker run healthy ≤5s. (1pt)

7. **Epic: E6 – Kubernetes & Helm**
Tasks (1pt each):
- E6-S1: Helm charts: Deployments, Services, ConfigMaps/Secrets, HPA. (1pt)
- E6-S2: Probes & resources; resilient to normal load (no OOM). (1pt)
- E6-S3: Namespace dev; labels/annotations complete. (1pt)

8. **Epic: E7 – Observability**
Tasks (1pt each):
- E7-S1: Prometheus scrape config for api/worker; targets up. (1pt)
- E7-S2: Grafana dashboards (p50/p95, RPS, error_rate, job throughput). (1pt)
- E7-S3: Loki+promtail; logs correlate with trace_id. (1pt)
- E7-S4: Alerts: error_rate>5% (5m); job_failures>0 (10m). (1pt)

9. **Epic: E8 – Security & Secrets**
Tasks (1pt each):
- E8-S1: sops+age encrypt secrets in git; decrypt locally. (1pt)
- E8-S2: Image scanning (trivy) + SBOM (syft); fail on CRITICAL. (1pt)
- E8-S3: Image signing (cosign) & verify step. (1pt)

10. **Epic: E9 – CI/CD**
Tasks (1pt each):
- E9-S1: Lint (ruff/black, shellcheck), unit & integration tests; coverage report. (1pt)
- E9-S2: Build & push images with tags gitsha and latest. (1pt)
- E9-S3: Deploy to kind via Helm; run smoke tests. (1pt)
- E9-S4: Cache deps; total runtime ≤10 min on small runner. (1pt)

11. **Epic: E10 – Python CLI (Typer) opsbox**
Tasks (1pt each):
- E10-S1: opsbox build, opsbox push. (1pt)
- E10-S2: opsbox deploy --env dev (Helm upgrade & wait). (1pt)
- E10-S3: opsbox smoke --url … (health + simple check). (1pt)
- E10-S4: opsbox logs --app api|worker. (1pt)
- E10-S5: opsbox rollback --app api. (1pt)

12. **Epic: E11 – Bash Scripts (strict mode)**
Tasks (1pt each):
- E11-S1: bootstrap.sh installs tools, starts kind, loads images. (1pt)
- E11-S2: pipeline_local.sh mirrors CI and fails fast. (1pt)
- E11-S3: cluster-up.sh, cluster-down.sh, port-forward.sh, smoke.sh. (1pt)

13. **Epic: E12 – Progressive Delivery**
Tasks (1pt each):
- E12-S1: Canary with Argo Rollouts or blue/green steps 10%→50%→100%. (1pt)
- E12-S2: Auto-rollback on SLO breach. (1pt)

14. **Epic: E13 – Environments**
Tasks (1pt each):
- E13-S1: dev values/secrets templatized; dev-only initially. (1pt)

15. **Epic: E14 – Testing**
Tasks (1pt each):
- E14-S1: Unit tests for API & worker (≥70% app code coverage). (1pt)
- E14-S2: Integration tests (DB/Redis via test containers) in CI. (1pt)
- E14-S3: E2E smoke post-deploy (CLI & pipeline). (1pt)
- E14-S4: Chaos test (kill pod) — app recovers. (1pt)

16. **Epic: E15 – Documentation & Runbooks**
Tasks (1pt each):
- E15-S1: README quickstart (5 min to first success). (1pt)
- E15-S2: Runbooks: Deploy, Rollback, On-call cheatsheet. (1pt)
- E15-S3: ADRs: FastAPI, RQ vs Celery, Rollouts, secrets tool (3–5). (1pt)

17. **Optional: map some backlog “smallest units” you haven’t covered as tasks**
Most backlog items map into the Epics above, but if you want explicit tasks for observability/security plumbing and Helm bits, you can also add:
 Prometheus Helm install/config (1pt).
 Grafana Helm + import dashboards JSON (1pt).
 Loki + promtail setup (1pt).
 Alert rule files committed (1pt).
 cosign sign/verify wiring in CI (1pt).
