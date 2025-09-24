# How it works

## Argo Rollout replaces a standard Deployment.

- It controls how new versions of your API are rolled out (e.g. 10% traffic → 50% → 100%).
- AnalysisTemplate defines automated checks (metrics, webhooks, jobs).
- In your case, you added an analysis that queries Prometheus for API error rate.
    - Args let you pass parameters (e.g. service name, window size, threshold).
    - That’s why you needed to quote 0.05 (threshold): Argo validates args as strings.

- During rollout Argo:
    - Deploys a small percentage of pods with the new image.
    - Runs the AnalysisTemplate against live metrics.

- If metrics are OK → promote to next step.
- If metrics fail (e.g., error rate > 5% for 5m) → rollback automatically.

## Benefits for OpsBox
1. **Safe releases**

- Instead of flipping from old → new all at once, traffic shifts gradually.
- If something breaks, only a slice of users see errors before rollback.

2. **Automated quality gates**

- You don’t need to manually babysit kubectl get pods.
- Rollout waits for metrics (latency, error rate, job failures) to prove health.

3. **Continuous delivery confidence**

- Fits directly into your CI/CD goal:
- “Safe releases: canary auto-promotes on good metrics; auto-rolls back on failures.”

4. **Observability integration**

- Ties directly to Prometheus, Grafana, Loki.
- The same metrics you visualize/alert on drive rollout decisions.

5. **Less on-call pain**

- Fewer “oh no, prod is broken” moments because a bad build gets stopped before full blast.

## Example in action

- You push a new API image (v2).
- Argo spins up 10% pods with v2.
- AnalysisTemplate checks:
    - /metrics → Prometheus query: error_rate < 5%

If ✅: traffic promoted to 50%, then 100%.
If ❌ (say error_rate = 20%):

## Argo halts rollout.

- Rolls back to last good ReplicaSet (v1).
- You get an event in Argo UI + Alertmanager.

## In short:

- It’s like having automated canary testing baked into Kubernetes. It reduces risk, enforces SLOs at deploy time, and lines up with your OpsBox success criteria for progressive delivery