# Adding Custom Grafana Dashboards to kube-prometheus-stack

This README walks you through **three reliable ways** to add your own Grafana dashboards when deploying the `prometheus-community/kube-prometheus-stack` Helm chart.

> Works for fresh installs and upgrades. Includes verification and troubleshooting.

---

## Prerequisites

* Helm 3.x
* kubectl configured to your cluster
* Namespace (example uses `monitoring`)
* Chart repo added

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
```

Set your release/namespace (optional):

```bash
export RELEASE=monitoring
export MONITORING_NAMESPACE=monitoring
```

---

## Option A — Embed dashboard JSON in a values file (GitOps-friendly)

Store dashboards inline inside a values file (e.g., `ops/observability/values.override.yaml`).

**values.override.yaml**

```yaml
grafana:
  sidecar:
    dashboards:
      enabled: true
  dashboards:
    default:
      my-dashboard.json: |
        {
          "id": null,
          "title": "My Custom Dashboard",
          "tags": ["k8s", "team-ops"],
          "timezone": "browser",
          "schemaVersion": 36,
          "version": 1,
          "panels": []
        }
```

**Install/Upgrade**

```bash
helm upgrade --install "$RELEASE" prometheus-community/kube-prometheus-stack \
  -n "$MONITORING_NAMESPACE" \
  -f ops/observability/values.override.yaml
```

Pros: versioned in Git, reproducible.
Cons: large JSON in YAML can be noisy.

---

## Option B — Use a ConfigMap and reference it (clean for teams)

Keep dashboards as separate JSON files and mount them via ConfigMap(s).

**1) Create ConfigMap(s)**

```bash
kubectl -n "$MONITORING_NAMESPACE" create configmap grafana-dashboard-ops \
  --from-file=my-dashboard.json=./dashboards/my-dashboard.json
```

**2) Reference in values**

```yaml
grafana:
  sidecar:
    dashboards:
      enabled: true
  dashboardsConfigMaps:
    ops: grafana-dashboard-ops
```

**3) Install/Upgrade**

```bash
helm upgrade --install "$RELEASE" prometheus-community/kube-prometheus-stack \
  -n "$MONITORING_NAMESPACE" \
  -f ops/observability/values.override.yaml
```

Pros: clean separation, easy to swap dashboards without editing YAML.
Cons: extra `kubectl` step to create/update ConfigMaps.

---

## Option C — Inject local files with `--set-file` (quick & scriptable)

If your dashboard JSON is on disk, inject it directly at install/upgrade time.

```bash
helm upgrade --install "$RELEASE" prometheus-community/kube-prometheus-stack \
  -n "$MONITORING_NAMESPACE" \
  --set grafana.sidecar.dashboards.enabled=true \
  --set-file grafana.dashboards.default.ops-overview.json=./dashboards/ops-overview.json
```

> **Important**: The last key must end with `.json` (e.g., `ops-overview.json`) so Grafana’s sidecar recognizes it as a dashboard file.

Pros: no temp files/ConfigMaps; great for one-offs and CI.
Cons: less explicit in Git history.

---

## Organizing by folder

You can group dashboards into folders by nesting under another key (folder name) beneath `grafana.dashboards`.

```yaml
grafana:
  dashboards:
    networking:
      ingress.json: |
        { "title": "Ingress", "tags": ["network"], "panels": [] }
    applications:
      api.json: |
        { "title": "API", "tags": ["api"], "panels": [] }
```

Grafana will create folders **networking** and **applications** and place dashboards accordingly.

---

## Adding tags to dashboards

Tags are defined **inside the dashboard JSON**:

```json
{
  "title": "Ops Overview",
  "tags": ["ops", "k8s", "prometheus"],
  "schemaVersion": 36,
  "panels": []
}
```

There is no separate Helm value for tags; they must be part of the dashboard object.

---

## Verifying the deployment

### 1) Check Helm values actually applied

```bash
helm get values "$RELEASE" -n "$MONITORING_NAMESPACE" -a
```

### 2) Inspect rendered manifests (dry run)

```bash
helm upgrade --install "$RELEASE" prometheus-community/kube-prometheus-stack \
  -n "$MONITORING_NAMESPACE" \
  -f ops/observability/values.override.yaml \
  --dry-run --debug | less
```

Look for a ConfigMap named like `RELEASE-grafana-dashboards` containing your `*.json` entries.

### 3) Check Grafana UI

* Open Grafana → **Dashboards → Browse**
* Find your dashboard (under **default** or the folder you specified)
* Use the Search or filter by tags

### 4) Confirm the sidecar is working

```bash
kubectl -n "$MONITORING_NAMESPACE" get pod -l app.kubernetes.io/name=grafana
kubectl -n "$MONITORING_NAMESPACE" logs deploy/"$RELEASE"-grafana -c grafana-sc-dashboard | tail -n 100
```

You should see logs indicating dashboards were discovered/imported.

---

## Common pitfalls & fixes

* **Pasting JSON with `--set`** → Use `--set-file` or a values file; `--set` can’t handle complex JSON.
* **Wrong value path** → Double-check with `helm show values prometheus-community/kube-prometheus-stack`.
* **Sidecar disabled** → Ensure `grafana.sidecar.dashboards.enabled=true`.
* **Arrays don’t merge** → Lists are replaced, not merged. Provide the full list you want.
* **Namespaces don’t match** → Ensure you’re checking the same namespace Helm deployed to. Watch out for `namespaceOverride`.

---

## Updating dashboards

### Option A (values file):

Edit the JSON under `grafana.dashboards` and run upgrade:

```bash
helm upgrade --install "$RELEASE" prometheus-community/kube-prometheus-stack \
  -n "$MONITORING_NAMESPACE" \
  -f ops/observability/values.override.yaml
```

### Option B (ConfigMap):

Update the ConfigMap from file and (optionally) restart Grafana if not auto-reloaded:

```bash
kubectl -n "$MONITORING_NAMESPACE" create configmap grafana-dashboard-ops \
  --from-file=my-dashboard.json=./dashboards/my-dashboard.json \
  -o yaml --dry-run=client | kubectl apply -f -
```

### Option C (`--set-file`):

Point to the updated file and run upgrade again.

---

## Rollback or uninstall

```bash
helm rollback "$RELEASE" 1 -n "$MONITORING_NAMESPACE"   # to a previous revision
helm uninstall "$RELEASE" -n "$MONITORING_NAMESPACE"    # remove release
```

---

## Minimal working example (copy/paste)

Create `ops/observability/values.override.yaml`:

```yaml
grafana:
  sidecar:
    dashboards:
      enabled: true
  dashboards:
    default:
      smoke-test.json: |
        {
          "title": "Smoke Test",
          "tags": ["demo"],
          "schemaVersion": 36,
          "version": 1,
          "panels": []
        }
```

Deploy:

```bash
helm upgrade --install "$RELEASE" prometheus-community/kube-prometheus-stack \
  -n "$MONITORING_NAMESPACE" \
  -f ops/observability/values.override.yaml
```

Verify in Grafana → Dashboards.

---

## Appendix: Using variables (templating) in dashboards

If your dashboards rely on variables (e.g., `namespace`, `datasource`), define them in the dashboard JSON under `templating.list`. Example snippet:

```json
{
  "templating": {
    "list": [
      {
        "name": "datasource",
        "type": "datasource",
        "query": "prometheus",
        "refresh": 1
      },
      {
        "name": "namespace",
        "type": "query",
        "label": "Namespace",
        "datasource": { "type": "prometheus", "uid": "$datasource" },
        "query": "label_values(kube_pod_info, namespace)",
        "refresh": 1
      }
    ]
  }
}
```
