# OpsBox — Advanced Practice Plan (Phase 2)

This document describes the advanced phase of OpsBox. It extends the base project to practice advanced DevOps skills in reliability, scaling, delivery safety, security, observability, compliance, and GitOps.

## Goals
- Push OpsBox into production-grade territory with advanced reliability and security features.
- Practice chaos engineering, automated rollbacks, GitOps, and compliance guardrails.

## Key Areas
1. **Reliability, Scaling & Performance**
   - KEDA + HPA for autoscaling on Redis queue depth.
   - Chaos experiments with pod disruptions, network faults.
   - Load tests with K6/Locust.

2. **Delivery Safety**
   - Advanced Argo Rollouts analysis for canaries with auto-rollback.
   - Feature flags via ConfigMaps.

3. **Security**
   - Cosign keyless signing + in-cluster admission checks.
   - Provenance attestations (SLSA).
   - OWASP ZAP and fuzzing in CI.
   - Gitleaks + pre-commit hooks for secret hygiene.

4. **Observability**
   - RED/USE dashboards as code.
   - Tail-based sampling with OpenTelemetry Collector.
   - SLOs + error budgets with burn-rate alerts.

5. **Compliance & Guardrails**
   - OPA Gatekeeper or Kyverno: disallow :latest, require limits, enforce signed images.
   - RBAC hardening with least privilege.

6. **Data Safety & DR**
   - Postgres backups to MinIO with restore drills.
   - Zero-downtime migrations (expand–migrate–contract).

7. **GitOps & Environments**
   - Argo CD for dev/staging with preview environments.
   - Image promotion via GitOps PRs.

8. **Cost & Logs**
   - Loki retention & index strategy.
   - Cost-ish signals in Grafana.

## Sprint Map
- **Week 1**: Autoscaling, rollouts with Prometheus analysis, dashboards.
- **Week 2**: Image signing, SBOM, provenance, policy enforcement.
- **Week 3**: Chaos, backups, migration drills.
- **Week 4**: GitOps setup, on-call runbooks.

## Example Task
**Enable KEDA for Worker**
- Add ScaledObject on Redis queue length.
- Produce 2k jobs → observe scale-out/in.

---
